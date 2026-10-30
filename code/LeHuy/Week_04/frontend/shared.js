'use strict';

// ==================== Trạng thái giao diện ====================

let ws = null;
let chosen = null;
let lastCreate = null;

let transitionBusy = false;
let createBusy = false;
let listBusy = false;

let nextCursor = null;
let sessionGeneration = 0;

// ==================== Trạng thái kết nối ====================

let connectionWanted = false;
let reconnectTimer = null;
let reconnectAttempts = 0;
let connectTimeout = null;
let heartbeatTimer = null;
let heartbeatBusy = false;

// URL chứa token chỉ được giữ trong bộ nhớ của trang.
let sessionUrl = null;

const MAX_RECONNECT_ATTEMPTS = 8;

const known = new Map();
const pending = new Map();

const $ = id => document.getElementById(id);

const orderStorageKey =
  'fooddelivery:lastOrder:' + window.location.pathname;

const statusLabels = {
  PLACED: 'Chờ tài xế nhận',
  ACCEPTED: 'Tài xế đã nhận',
  DELIVERING: 'Đang giao',
  COMPLETED: 'Đã hoàn tất'
};

const terminalWorkflowStatuses = new Set([
  'SUCCEEDED',
  'FAILED',
  'TIMED_OUT',
  'ABORTED'
]);

// ==================== Tiện ích ====================

function log(message) {
  const element = $('log');
  if (!element) return;

  const line = new Date().toISOString() + ' ' + message;
  const lines = (element.textContent + line + '\n').split('\n');

  element.textContent = lines.slice(-500).join('\n');
  element.scrollTop = element.scrollHeight;
}

function rid() {
  return globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID()
    : 'REQ-' + Date.now() + '-' +
        Math.random().toString(36).slice(2);
}

function connected() {
  return ws?.readyState === WebSocket.OPEN;
}

function selectedOrderId() {
  return $('order')?.value.trim() || '';
}

function setConnectionStatus(value) {
  if ($('connection')) {
    $('connection').textContent = value;
  }
}

function isOrderTerminal(order) {
  return Boolean(
    order && (
      order.status === 'COMPLETED' ||
      terminalWorkflowStatuses.has(order.workflowStatus) ||
      terminalWorkflowStatuses.has(order.executionStatus)
    )
  );
}

function workflowLabel(order) {
  // Nhánh timeout của workflow dùng state Fail nên execution có thể
  // là FAILED, trong khi Orders lưu nguyên nhân chính là TIMED_OUT.
  if (
    order.workflowStatus === 'TIMED_OUT' ||
    order.executionStatus === 'TIMED_OUT'
  ) {
    return 'Hết thời gian chờ xử lý';
  }

  if (
    order.workflowStatus === 'FAILED' ||
    order.executionStatus === 'FAILED'
  ) {
    return 'Luồng xử lý gặp lỗi';
  }

  if (
    order.workflowStatus === 'ABORTED' ||
    order.executionStatus === 'ABORTED'
  ) {
    return 'Luồng xử lý đã bị dừng';
  }

  if (
    order.status === 'COMPLETED' ||
    order.workflowStatus === 'SUCCEEDED' ||
    order.executionStatus === 'SUCCEEDED'
  ) {
    return 'Đơn hàng đã hoàn tất';
  }

  return 'Luồng xử lý đang hoạt động';
}

// Chỉ lưu mã đơn, không lưu token.
function rememberOrder(orderId) {
  try {
    const value = String(orderId || '').trim();

    if (value) {
      sessionStorage.setItem(orderStorageKey, value);
    } else {
      sessionStorage.removeItem(orderStorageKey);
    }
  } catch {
    log('STORAGE_ERROR: không thể lưu mã đơn.');
  }
}

function restoreOrder() {
  try {
    const saved = sessionStorage.getItem(orderStorageKey);

    if (saved && $('order')) {
      $('order').value = saved;
    }
  } catch {
    log('STORAGE_ERROR: không thể khôi phục mã đơn.');
  }
}

// ==================== Hiển thị và khóa nút ====================

function refreshButtons() {
  const online = connected();

  const socketActive =
    ws !== null && ws.readyState !== WebSocket.CLOSED;

  if ($('connectButton')) {
    $('connectButton').disabled =
      socketActive || connectionWanted;
  }

  if ($('disconnectButton')) {
    $('disconnectButton').disabled =
      !socketActive && !connectionWanted;
  }

  document.querySelectorAll('[data-online]').forEach(button => {
    button.disabled = !online;
  });

  if ($('createButton')) {
    $('createButton').disabled = !online || createBusy;
  }

  if ($('retryButton')) {
    $('retryButton').disabled =
      !online || createBusy || !lastCreate;
  }

  if ($('listButton')) {
    $('listButton').disabled = !online || listBusy;
  }

  if ($('next')) {
    $('next').disabled = !online || listBusy || !nextCursor;
  }

  const ready = Array.isArray(chosen?.readySteps)
    ? chosen.readySteps
    : [];

  const correctOrder =
    chosen?.orderId === selectedOrderId();

  const transitions = [
    ['accept', 'ACCEPTED', 'PLACED'],
    ['deliver', 'DELIVERING', 'ACCEPTED'],
    ['complete', 'COMPLETED', 'DELIVERING']
  ];

  for (const [buttonId, target, previous] of transitions) {
    const button = $(buttonId);
    if (!button) continue;

    button.disabled = !(
      online &&
      !transitionBusy &&
      correctOrder &&
      !isOrderTerminal(chosen) &&
      chosen?.status === previous &&
      ready.includes(target)
    );
  }
}

function clearSelected(message = 'Chưa chọn đơn') {
  chosen = null;

  if ($('snapshot')) {
    $('snapshot').textContent = message;
  }

  if ($('progress')) {
    $('progress').textContent = '';
  }

  refreshButtons();
}

function render(data) {
  if (
    !data ||
    typeof data.orderId !== 'string' ||
    !Number.isInteger(data.version) ||
    data.version < 1 ||
    !Object.prototype.hasOwnProperty.call(statusLabels, data.status)
  ) {
    return;
  }

  const old = known.get(data.orderId);

  if (old && data.version < old.version) {
    log(
      'IGNORED_OLD_VERSION orderId=' + data.orderId +
      ' received=' + data.version +
      ' current=' + old.version
    );
    return;
  }

  if (
    old &&
    data.version === old.version &&
    data.status !== old.status
  ) {
    log('IGNORED_INCONSISTENT_STATUS orderId=' + data.orderId);
    return;
  }

  const current =
    old && data.version === old.version
      ? { ...old, ...data }
      : { ...data };

  // Trạng thái workflow có thể đổi mà version nghiệp vụ không tăng.
  // Không để phản hồi cũ cùng version làm mất trạng thái kết thúc.
  if (old && data.version === old.version) {
    if (
      terminalWorkflowStatuses.has(old.workflowStatus) &&
      !terminalWorkflowStatuses.has(current.workflowStatus)
    ) {
      current.workflowStatus = old.workflowStatus;
    }

    if (
      terminalWorkflowStatuses.has(old.executionStatus) &&
      !terminalWorkflowStatuses.has(current.executionStatus)
    ) {
      current.executionStatus = old.executionStatus;
    }
  }

  if (isOrderTerminal(current)) {
    current.readySteps = [];
  }

  known.set(data.orderId, current);

  if (selectedOrderId() !== data.orderId) return;

  rememberOrder(data.orderId);
  chosen = current;

  if ($('snapshot')) {
    $('snapshot').textContent = JSON.stringify(current, null, 2);
  }

  if ($('progress')) {
    $('progress').textContent =
      statusLabels[current.status] +
      ' | ' + workflowLabel(current) +
      ' | phiên bản ' + current.version +
      (current.driverId ? ' | tài xế ' + current.driverId : '');
  }

  if (
    isOrderTerminal(current) &&
    (!old || !isOrderTerminal(old))
  ) {
    log(
      'ORDER_TERMINAL orderId=' + current.orderId +
      ' status=' + current.status +
      ' workflowStatus=' + (current.workflowStatus || 'UNKNOWN') +
      ' executionStatus=' + (current.executionStatus || 'UNKNOWN') +
      '; dừng đọc định kỳ và khóa các nút chuyển trạng thái.'
    );
  }

  refreshButtons();
}

// ==================== Gửi và nhận yêu cầu ====================

function rejectPending(message) {
  for (const item of pending.values()) {
    clearTimeout(item.timer);
    item.reject(new Error(message));
  }

  pending.clear();
}

function send(body) {
  return new Promise((resolve, reject) => {
    if (!connected()) {
      reject(new Error('Chưa kết nối WebSocket.'));
      return;
    }

    const request = {
      ...body,
      requestId: body.requestId || rid()
    };

    if (pending.has(request.requestId)) {
      reject(new Error('Yêu cầu này đang chờ phản hồi.'));
      return;
    }

    const timer = setTimeout(() => {
      pending.delete(request.requestId);

      reject(new Error(
        'Chưa nhận phản hồi sau 30 giây. ' +
        'Kiểm tra trạng thái trước khi gửi lại.'
      ));
    }, 30000);

    pending.set(request.requestId, {
      resolve,
      reject,
      timer,
      action: request.action,
      orderId: request.orderId
    });

    try {
      ws.send(JSON.stringify(request));

      // Không ghi token, món ăn hoặc địa chỉ vào nhật ký gửi.
      log('SENT ' + JSON.stringify({
        action: request.action,
        requestId: request.requestId,
        orderId: request.orderId,
        targetStatus: request.targetStatus,
        expectedVersion: request.expectedVersion
      }));
    } catch {
      clearTimeout(timer);
      pending.delete(request.requestId);
      reject(new Error('Không gửi được yêu cầu.'));
    }
  });
}

async function perform(body) {
  const generation = sessionGeneration;

  try {
    const result = await send(body);

    if (generation !== sessionGeneration) return null;

    if (result?.orderId && result?.status) {
      render(result);
    }

    return result;
  } catch (error) {
    if (generation !== sessionGeneration) return null;

    log('ERROR ' + error.message);

    if (
      ['FORBIDDEN', 'UNAUTHORIZED', 'NOT_FOUND'].includes(error.message) &&
      body.orderId === selectedOrderId()
    ) {
      known.delete(body.orderId);
      clearSelected('Không thể truy cập đơn: ' + error.message);
    }

    return null;
  }
}

// ==================== Quản lý kết nối ====================

function clearConnectionTimers() {
  clearTimeout(connectTimeout);
  clearInterval(heartbeatTimer);

  connectTimeout = null;
  heartbeatTimer = null;
  heartbeatBusy = false;
}

function resetConnectionData(message) {
  sessionGeneration += 1;
  rejectPending(message);

  known.clear();
  nextCursor = null;
  transitionBusy = false;
  createBusy = false;
  listBusy = false;

  if ($('list')) {
    $('list').textContent =
      'Bấm Tải trang đầu sau khi kết nối lại.';
  }

  clearSelected(message);
}

function stopSocket(message) {
  clearConnectionTimers();

  const oldSocket = ws;
  ws = null;

  if (
    oldSocket &&
    oldSocket.readyState !== WebSocket.CLOSED
  ) {
    try {
      oldSocket.close(4000, 'Connection reset');
    } catch {
      // Callback của socket cũ sẽ bị bỏ qua.
    }
  }

  resetConnectionData(message);
}

function scheduleReconnect() {
  if (!connectionWanted || !sessionUrl || reconnectTimer) {
    return;
  }

  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    connectionWanted = false;
    sessionUrl = null;

    setConnectionStatus('CLOSED');

    log(
      'RECONNECT_STOPPED: đã thử lại ' +
      MAX_RECONNECT_ATTEMPTS +
      ' lần. Kiểm tra mạng, endpoint, token rồi bấm Kết nối.'
    );

    refreshButtons();
    return;
  }

  if (navigator.onLine === false) {
    setConnectionStatus('OFFLINE');
    log('OFFLINE: chờ mạng trở lại.');
    refreshButtons();
    return;
  }

  const delay = Math.min(
    1000 * (2 ** reconnectAttempts),
    30000
  );

  reconnectAttempts += 1;
  setConnectionStatus('RECONNECTING');

  log(
    'RECONNECT_SCHEDULED attempt=' +
    reconnectAttempts +
    '/' + MAX_RECONNECT_ATTEMPTS +
    ' delay=' + (delay / 1000) + 's'
  );

  refreshButtons();

  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;

    if (connectionWanted) {
      openSocket();
    }
  }, delay);
}

function startHeartbeat(socket) {
  clearInterval(heartbeatTimer);

  heartbeatTimer = setInterval(async () => {
    if (
      ws !== socket ||
      !connected() ||
      heartbeatBusy
    ) {
      return;
    }

    heartbeatBusy = true;

    try {
      const data = await send({ action: 'ping' });

      if (ws !== socket) return;

      if (data?.message !== 'pong') {
        throw new Error('INVALID_HEARTBEAT');
      }
    } catch (error) {
      if (ws !== socket) return;

      if (error.message === 'UNAUTHORIZED') {
        log('SESSION_EXPIRED: nhập lại token và kết nối.');
        disconnect();
        return;
      }

      log('HEARTBEAT_FAILED: thử khôi phục kết nối.');

      stopSocket('Mất phản hồi từ máy chủ. Đang kết nối lại...');
      scheduleReconnect();
    } finally {
      if (ws === socket) {
        heartbeatBusy = false;
      }
    }
  }, 15000);
}

function openSocket() {
  if (!connectionWanted || !sessionUrl) return;

  if (ws && ws.readyState !== WebSocket.CLOSED) return;

  if (navigator.onLine === false) {
    setConnectionStatus('OFFLINE');
    refreshButtons();
    return;
  }

  let socket;

  try {
    socket = new WebSocket(sessionUrl);
  } catch {
    log('CONNECT_ERROR: không thể khởi tạo WebSocket.');
    scheduleReconnect();
    return;
  }

  ws = socket;

  setConnectionStatus(
    reconnectAttempts > 0 ? 'RECONNECTING' : 'CONNECTING'
  );

  clearSelected('Đang kết nối và chờ lấy lại dữ liệu đơn...');
  refreshButtons();

  connectTimeout = setTimeout(() => {
    if (
      ws !== socket ||
      socket.readyState === WebSocket.OPEN
    ) {
      return;
    }

    log('CONNECT_TIMEOUT');

    stopSocket('Kết nối quá thời gian chờ. Đang thử lại...');
    scheduleReconnect();
  }, 15000);

  socket.onopen = async () => {
    if (ws !== socket) return;

    clearTimeout(connectTimeout);
    connectTimeout = null;
    reconnectAttempts = 0;

    setConnectionStatus('OPEN');

    log('OPEN');
    refreshButtons();
    startHeartbeat(socket);

    // Kết nối mới phải đăng ký theo dõi lại và đọc snapshot.
    // Không tự gửi lại thao tác tạo đơn hoặc chuyển trạng thái.
    if (selectedOrderId()) {
      log('RESUBSCRIBE orderId=' + selectedOrderId());

      const data = await watch();

      if (ws !== socket) return;

      if (data?.orderId && data?.status) {
        log(
          'SNAPSHOT_RESTORED orderId=' + data.orderId +
          ' status=' + data.status +
          ' version=' + data.version
        );
      } else {
        log(
          'RESUBSCRIBE_FAILED: kiểm tra lỗi rồi bấm Theo dõi đơn.'
        );
      }
    } else {
      clearSelected('Đã kết nối. Hãy tạo hoặc chọn đơn.');
    }
  };

  socket.onmessage = event => {
    if (ws !== socket) return;

    let message;

    try {
      message = JSON.parse(event.data);
    } catch {
      log('INVALID_RESPONSE: phản hồi không phải JSON.');
      return;
    }

    if (
      !message ||
      typeof message !== 'object' ||
      Array.isArray(message)
    ) {
      log('INVALID_RESPONSE: cấu trúc phản hồi không hợp lệ.');
      return;
    }

    log('RECEIVED ' + JSON.stringify(message));

    if (message.type === 'ORDER_UPDATED') {
      render(message);
      return;
    }

    if (message.type !== 'RESPONSE') return;

    const item = pending.get(message.requestId);
    if (!item) return;

    clearTimeout(item.timer);
    pending.delete(message.requestId);

    if (message.ok === true) {
      item.resolve(message.data);
    } else {
      item.reject(new Error(message.error?.code || 'UNKNOWN'));
    }
  };

  socket.onclose = event => {
    if (ws !== socket) return;

    clearConnectionTimers();
    ws = null;

    log('CLOSED code=' + event.code);

    resetConnectionData(
      connectionWanted
        ? 'Kết nối bị gián đoạn. Đang chờ kết nối lại...'
        : 'Đã ngắt kết nối.'
    );

    setConnectionStatus('CLOSED');

    if (connectionWanted) {
      scheduleReconnect();
    } else {
      refreshButtons();
    }
  };

  socket.onerror = () => {
    if (ws !== socket) return;

    log(
      'CONNECT_ERROR: kiểm tra mạng, endpoint, token và log Lambda.'
    );
  };
}

function connect() {
  if (
    connectionWanted ||
    (ws && ws.readyState !== WebSocket.CLOSED)
  ) {
    log('Hãy bấm Ngắt trước khi tạo phiên kết nối mới.');
    return;
  }

  let url;

  try {
    url = new URL($('endpoint').value.trim());

    if (
      url.protocol !== 'wss:' ||
      url.username ||
      url.password ||
      url.hash
    ) {
      throw new Error();
    }
  } catch {
    log('Endpoint phải là URL wss:// hợp lệ.');
    return;
  }

  const token = $('token').value;

  if (!token.trim()) {
    log('Nhập token phiên thử.');
    return;
  }

  url.searchParams.set('token', token);

  sessionUrl = url.toString();
  connectionWanted = true;
  reconnectAttempts = 0;

  clearTimeout(reconnectTimer);
  reconnectTimer = null;

  // Phiên mới không sử dụng yêu cầu tạo đơn của phiên cũ.
  lastCreate = null;

  resetConnectionData('Đang mở phiên kết nối mới...');
  openSocket();
}

function disconnect() {
  connectionWanted = false;
  sessionUrl = null;
  reconnectAttempts = 0;

  clearTimeout(reconnectTimer);
  reconnectTimer = null;

  stopSocket('Đã ngắt kết nối chủ động.');

  lastCreate = null;

  setConnectionStatus('CLOSED');

  log('DISCONNECTED_BY_USER: không tự kết nối lại.');
  refreshButtons();
}

window.addEventListener('offline', () => {
  if (!connectionWanted) return;

  clearTimeout(reconnectTimer);
  reconnectTimer = null;

  stopSocket('Mất mạng. Chờ mạng trở lại để kết nối lại.');

  setConnectionStatus('OFFLINE');

  log('OFFLINE');
  refreshButtons();
});

window.addEventListener('online', () => {
  if (!connectionWanted) return;

  log('ONLINE: chuẩn bị kết nối lại.');
  scheduleReconnect();
});

// ==================== Đọc và theo dõi đơn ====================

async function readOrder() {
  const orderId = selectedOrderId();

  if (!orderId) {
    log('Nhập mã đơn trước.');
    return null;
  }

  return perform({
    action: 'getOrder',
    orderId
  });
}

async function watch() {
  const orderId = selectedOrderId();

  if (!orderId) {
    log('Nhập mã đơn trước.');
    return null;
  }

  rememberOrder(orderId);

  if (chosen?.orderId !== orderId) {
    clearSelected('Đang lấy dữ liệu và đăng ký theo dõi đơn...');
  }

  return perform({
    action: 'subscribeOrder',
    orderId
  });
}

// ==================== Giao diện khách hàng ====================

async function createOrder() {
  if (createBusy) return;

  if (!connected()) {
    log('Kết nối WebSocket trước.');
    return;
  }

  const name = $('food').value.trim();
  const quantity = Number($('quantity').value);
  const deliveryAddress = $('address').value.trim();

  if (
    name.length < 1 ||
    name.length > 100 ||
    !Number.isInteger(quantity) ||
    quantity < 1 ||
    quantity > 20 ||
    deliveryAddress.length < 5 ||
    deliveryAddress.length > 300
  ) {
    log(
      'Dữ liệu không hợp lệ: tên món 1–100 ký tự, ' +
      'số lượng nguyên 1–20, địa chỉ 5–300 ký tự.'
    );
    return;
  }

  lastCreate = {
    action: 'createOrder',
    requestId: rid(),
    items: [{ name, quantity }],
    deliveryAddress
  };

  await retryCreate();
}

async function retryCreate() {
  if (createBusy) return;

  if (!lastCreate) {
    log('Chưa có yêu cầu tạo đơn để gửi lại.');
    return;
  }

  const generation = sessionGeneration;

  createBusy = true;
  refreshButtons();

  try {
    const data = await perform(lastCreate);

    if (generation !== sessionGeneration) return;

    if (data?.orderId) {
      $('order').value = data.orderId;
      rememberOrder(data.orderId);

      chosen = null;
      render(data);

      await watch();
    }
  } finally {
    if (generation === sessionGeneration) {
      createBusy = false;
      refreshButtons();
    }
  }
}

// ==================== Giao diện tài xế ====================

async function listOrders(cursor = null) {
  if (listBusy || !$('list')) return;

  const generation = sessionGeneration;

  listBusy = true;
  $('list').textContent = 'Đang tải danh sách...';

  refreshButtons();

  try {
    const data = await perform({
      action: 'listOrders',
      cursor
    });

    if (generation !== sessionGeneration) return;

    if (!data || !Array.isArray(data.orders)) {
      $('list').textContent = 'Không tải được danh sách đơn.';
      return;
    }

    nextCursor = data.nextCursor || null;

    if ($('next')) {
      $('next').onclick = () => listOrders(nextCursor);
    }

    const list = $('list');
    list.textContent = '';

    for (const order of data.orders) {
      const row = document.createElement('p');
      const button = document.createElement('button');

      row.textContent =
        order.orderId + ' | ' +
        order.status + ' | v' +
        order.version +
        (order.driverId ? ' | ' + order.driverId : '') +
        (order.workflowStatus
          ? ' | workflow: ' + order.workflowStatus
          : '') +
        ' ';

      button.textContent = 'Mở';

      button.onclick = async () => {
        if (generation !== sessionGeneration) return;

        $('order').value = order.orderId;
        rememberOrder(order.orderId);

        clearSelected('Đang mở đơn...');
        await watch();
      };

      row.append(button);
      list.append(row);
    }

    if (!data.orders.length) {
      list.textContent =
        'Không có đơn phù hợp trên trang này. ' +
        'Kiểm tra trang tiếp theo nếu có.';
    }
  } finally {
    if (generation === sessionGeneration) {
      listBusy = false;
      refreshButtons();
    }
  }
}

async function transition(target) {
  if (transitionBusy) return;

  if (
    !connected() ||
    !chosen ||
    chosen.orderId !== selectedOrderId()
  ) {
    log('Kết nối và chọn đúng đơn trước.');
    return;
  }

  if (isOrderTerminal(chosen)) {
    log('Đơn đã kết thúc. Không thể chuyển trạng thái.');
    refreshButtons();
    return;
  }

  const previous = {
    ACCEPTED: 'PLACED',
    DELIVERING: 'ACCEPTED',
    COMPLETED: 'DELIVERING'
  };

  const ready = Array.isArray(chosen.readySteps)
    ? chosen.readySteps
    : [];

  if (
    !Object.prototype.hasOwnProperty.call(previous, target) ||
    chosen.status !== previous[target] ||
    !ready.includes(target)
  ) {
    log('Bước này chưa sẵn sàng. Hãy đọc lại đơn.');
    return;
  }

  const generation = sessionGeneration;
  const orderId = chosen.orderId;

  const request = {
    action: 'updateOrderStatus',
    orderId,
    targetStatus: target,
    expectedVersion: chosen.version,
    requestId: rid()
  };

  transitionBusy = true;
  refreshButtons();

  try {
    const data = await send(request);

    if (generation !== sessionGeneration) return;

    log(
      'SUBMISSION ' + (data?.submission || 'UNKNOWN') +
      '; chờ dữ liệu đã commit.'
    );
  } catch (error) {
    if (generation !== sessionGeneration) return;

    log('ERROR ' + error.message);

    if (error.message === 'CONFLICT') {
      log(
        'CONFLICT_RECOVERY orderId=' + orderId +
        '; đọc lại snapshot hiện tại, không tự gửi lại thao tác.'
      );
    }
  } finally {
    if (generation === sessionGeneration) {
      try {
        // Luôn đọc lại sau thao tác, kể cả khi polling đang tắt.
        if (connected() && selectedOrderId() === orderId) {
          const fresh = await readOrder();

          if (
            generation === sessionGeneration &&
            selectedOrderId() === orderId
          ) {
            if (fresh) {
              log(
                'SNAPSHOT_REFRESHED orderId=' + fresh.orderId +
                ' status=' + fresh.status +
                ' version=' + fresh.version
              );
            } else {
              clearSelected(
                'Chưa xác nhận được trạng thái. ' +
                'Bấm Đọc đơn để kiểm tra.'
              );
            }
          }
        }
      } finally {
        if (generation === sessionGeneration) {
          transitionBusy = false;
          refreshButtons();
        }
      }
    }
  }
}

// ==================== Khởi tạo trang ====================

// Nhập mã đơn khác sẽ xóa snapshot cũ và khóa các nút chuyển bước.
$('order')?.addEventListener('input', () => {
  rememberOrder(selectedOrderId());

  clearSelected(
    'Bấm Đọc đơn hoặc Theo dõi đơn để lấy dữ liệu.'
  );
});

$('auto')?.addEventListener('change', () => {
  log(
    $('auto').checked
      ? 'POLLING_ENABLED: bật kiểm tra đơn định kỳ.'
      : 'POLLING_DISABLED: tắt kiểm tra đơn định kỳ.'
  );
});

restoreOrder();

if (selectedOrderId()) {
  clearSelected(
    'Đã khôi phục mã đơn. Nhập endpoint, token và bấm Kết nối.'
  );
}

// Kiểm tra bước chờ mỗi 3 giây khi bật ô auto.
// Không đọc định kỳ khi đơn đã kết thúc.
// Heartbeat là ping giữ kết nối, không phải yêu cầu đọc đơn.
setInterval(() => {
  const orderId = selectedOrderId();

  const readingThisOrder = [...pending.values()].some(item =>
    item.orderId === orderId &&
    ['getOrder', 'subscribeOrder'].includes(item.action)
  );

  if (
    $('auto')?.checked &&
    connected() &&
    !transitionBusy &&
    orderId &&
    chosen?.orderId === orderId &&
    !isOrderTerminal(chosen) &&
    !readingThisOrder
  ) {
    readOrder();
  }
}, 3000);

refreshButtons();