let ws=null, chosen=null, lastCreate=null;
const known=new Map(), pending=new Map();
const $=id=>document.getElementById(id);
function log(s){$('log').textContent+=new Date().toISOString()+' '+s+'\n';}
function rid(){return crypto.randomUUID ? crypto.randomUUID() : 'REQ-'+Date.now()+'-'+Math.random();}
function refreshButtons(){
 if(!$('accept'))return;
 const ready=chosen?.readySteps||[];
 for(const [id,target,prev] of [['accept','ACCEPTED','PLACED'],
   ['deliver','DELIVERING','ACCEPTED'],['complete','COMPLETED','DELIVERING']]){
  $(id).disabled=!(ws?.readyState===WebSocket.OPEN && chosen?.status===prev && ready.includes(target));
 }
}
function render(data){
 if(!data?.orderId)return;
 const old=known.get(data.orderId);
 if(old && Number(data.version)<Number(old.version))return;
 const current=old && Number(data.version)===Number(old.version)?{...old,...data}:{...data};
 known.set(data.orderId,current);
 if($('order').value===data.orderId){
  chosen=current;
  $('snapshot').textContent=JSON.stringify(current,null,2);
  refreshButtons();
 }
}
function send(body){
 return new Promise((resolve,reject)=>{
  if(ws?.readyState!==WebSocket.OPEN)return reject(new Error('Chưa kết nối'));
  if(!body.requestId)body.requestId=rid();
  if(pending.has(body.requestId))return reject(new Error('Yêu cầu đang chờ phản hồi, chưa gửi lặp lúc này.'));
  const timer=setTimeout(()=>{pending.delete(body.requestId);reject(new Error('Chưa nhận phản hồi. Kiểm tra rồi gửi lại cùng requestId.'));},30000);
  pending.set(body.requestId,{resolve,reject,timer});
  ws.send(JSON.stringify(body));log('SENT '+JSON.stringify(body));
 });
}
async function perform(body){
 try{
  const result=await send(body);
  if(result.orderId)render(result);
  return result;
 }catch(e){log('ERROR '+e.message);return null;}
}
function connect(){
 if(ws && ws.readyState!==WebSocket.CLOSED){log('Hãy ngắt kết nối trước');return;}
 let url;
 try{url=new URL($('endpoint').value.trim());if(url.protocol!=='wss:')throw Error();}
 catch{log('Endpoint phải là URL wss:// hợp lệ');return;}
 if(!$('token').value){log('Nhập token phiên thử');return;}
 url.searchParams.set('token',$('token').value);
 ws=new WebSocket(url.toString());
 ws.onopen=async()=>{
  $('connection').textContent='OPEN';log('OPEN');refreshButtons();
  if($('order').value)await watch();
 };
 ws.onmessage=e=>{
  let message;try{message=JSON.parse(e.data);}catch{log('INVALID_RESPONSE');return;}
  log('RECEIVED '+JSON.stringify(message));
  if(message.type==='ORDER_UPDATED')render(message);
  const p=pending.get(message.requestId);
  if(p){clearTimeout(p.timer);pending.delete(message.requestId);
   message.ok?p.resolve(message.data):p.reject(new Error(message.error?.code||'UNKNOWN'));
  }
 };
 ws.onclose=()=>{
  $('connection').textContent='CLOSED';log('CLOSED');refreshButtons();
  for(const p of pending.values()){clearTimeout(p.timer);p.reject(new Error('Kết nối đã đóng'));}
  pending.clear();
 };
 ws.onerror=()=>log('CONNECT_ERROR: kiểm tra endpoint, token và log Lambda');
}
function disconnect(){ws?.close();}
async function readOrder(){return perform({action:'getOrder',orderId:$('order').value.trim()});}
async function watch(){return perform({action:'subscribeOrder',orderId:$('order').value.trim()});}
async function createOrder(){
 lastCreate={action:'createOrder',requestId:rid(),items:[{name:$('food').value.trim(),
  quantity:Number($('quantity').value)}],deliveryAddress:$('address').value.trim()};
 await retryCreate();
}
async function retryCreate(){
 if(!lastCreate){log('Chưa có yêu cầu tạo đơn để gửi lại');return;}
 const data=await perform(lastCreate);
 if(data?.orderId){$('order').value=data.orderId;render(data);await watch();}
}
async function listOrders(cursor=null){
 const data=await perform({action:'listOrders',cursor});if(!data)return;
 $('next').disabled=!data.nextCursor;$('next').onclick=()=>listOrders(data.nextCursor);
 const list=$('list');list.textContent='';
 for(const order of data.orders){
  const p=document.createElement('p'),button=document.createElement('button');
  button.textContent='Mở';button.onclick=async()=>{$('order').value=order.orderId;await watch();};
  p.textContent=order.orderId+' | '+order.status+' | v'+order.version+' ';p.append(button);list.append(p);
 }
 if(!data.orders.length)list.textContent='Không có đơn phù hợp trên trang này. Kiểm tra trang tiếp theo nếu có.';
}
async function transition(target){
 if(!chosen){log('Chọn đơn trước');return;}
 const data=await perform({action:'updateOrderStatus',orderId:chosen.orderId,
   targetStatus:target,expectedVersion:Number(chosen.version),requestId:rid()});
 if(data){log('SUBMISSION '+data.submission+'; chờ dữ liệu đã commit');await readOrder();}
}
setInterval(()=>{
 if($('auto')?.checked && ws?.readyState===WebSocket.OPEN && $('order').value && chosen?.status!=='COMPLETED')readOrder();
},3000);
