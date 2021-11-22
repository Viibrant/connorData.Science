var socket = io();
socket.on("connect", function() {
  socket.emit("loaded");
});

socket.onAny(function(newCases) {
  alert(data);
});
