
// import the modules
var m_app = b4w.require("app");
var m_data = b4w.require("data");
var m_scenes = b4w.require("scenes");
var m_controls = b4w.require("controls");
var m_trans = b4w.require("transform");
var m_util = b4w.require("util");

// Some constants
var tower_ang_rate_limit_per_second = 3.6; // deg/sec limit to how fast the tower can move
var blade_ang_rate_limit_per_second = 7.6; // deg/sec limit to how fast the tower can move


// state variables
var cmd_pitch = 0.0;
var cmd_yaw = 0.0;
var cmd_rpm = 0.0;
var cur_pitch = 0.0;
var cur_yaw = 0.0;
var power = 0.0;
var wind_dir = 0.0;
var wind_speed = 0.0;
var air_density = 0.0;

var blades = new Array();

var socket = null;

function send_message(msg_obj){
  if (socket != null) {
    var jstring = JSON.stringify(msg_obj);
    socket.send(jstring);
  }
}

function clamp_send(id,min,max) {
  var name = id.substring(1);
  var value = $(id).val();
  if (!isNaN(value)) {
    value = Number(value);
    var msg = new Object;
    if (value > max)
      value = max;
    if (value < min)
      value = min;
    $(id).val(value);
    //alert("Change Wind Value to: " + value);
    msg[name]=value;
    send_message(msg);
  }
  else {
    alert("The value for " + name + " needs to be a number between " + min + " and " + max);
  }
}

function isN_send(id) {
  var name = id.substring(1);
  var value = $(id).val();
  if (!isNaN(value)) {
    value = Number(value);
    var msg = new Object;
    msg[name]=value;
    send_message(msg);
  }
  else {
    alert("The value for " + name + " needs to be a number.");
  }
}

function doneTypingClampSend(id,min,max) {
  var timer = null;
  //$(id).attr('timer',timer);
  $(id).keydown(function() {
    clearTimeout(timer);
    timer = setTimeout(function() {
      clamp_send(id,min,max);
    }, 1000);
  });
}

function doneTypingNumberSend(id) {
  var timer = null;
  //$(id).attr('timer',timer);
  $(id).keydown(function() {
    clearTimeout(timer);
    timer = setTimeout(function() {
      isN_send(id);
    }, 1000);
  });
}

function toggleStateSend(id){
  $( id ).click(function() {
      var text = $(id).text();
      var name = id.substring(1);
      if (text.indexOf('True') > 0) {
        text = text.replace("True", "False");
        $(id).text(text);
        var msg = new Object;
        msg[name]=false;
        send_message(msg);
      }
      else if (text.indexOf('False') > 0) {
        text = text.replace("False", "True");
        $(id).text(text);
        var msg = new Object;
        msg[name]=true;
        send_message(msg);
      }
      else {
        console.log("Error: Button label doesn't contain True or False");
      }
  });
}

// modify weather
doneTypingClampSend('#wind_dir_mod',0,360);
doneTypingClampSend('#wind_speed_mod',0,25);
doneTypingClampSend('#air_density_mod',1.1,1.552);
// should be class based
doneTypingNumberSend('#param_a');
doneTypingNumberSend('#param_b');
doneTypingNumberSend('#param_c');
doneTypingNumberSend('#param_d');
doneTypingNumberSend('#param_e');
doneTypingNumberSend('#param_f');
// toggle and send
toggleStateSend('#toggle_1_btn');
toggleStateSend('#toggle_2_btn');
toggleStateSend('#toggle_3_btn');
toggleStateSend('#toggle_4_btn');
toggleStateSend('#toggle_5_btn');
toggleStateSend('#toggle_6_btn');


$( '#clear_control_msg' ).click(function() {
   $('#control_msg').empty();
});

m_app.init({
    canvas_container_id: "wind-viz",
    callback: load_cb,
    autoresize: true
})

function load_cb() {
    m_data.load("windTurbine4.json", loaded_cb);
}

function rotorhub_cb(obj, id) {
  var elapsed = m_controls.get_sensor_value(obj, id, 0);
  rad_per_second = (cmd_rpm/60.0) * 2 * 3.14159265359;
  m_trans.rotate_x_local(obj, rad_per_second * elapsed);
  $("#rpm").html(cmd_rpm.toFixed(2));
}


function cntrl(cmd,cur,elapsed,rate_limit){
  // rate_limit units degrees per second
  // elpased is amount of time since last frame
  angle_error = cmd - cur;
  rate = angle_error/elapsed;
  if (Math.abs(rate) > rate_limit) {
    if (rate >= 0){
      angle_deg = rate_limit * elapsed;
    }
    else {
      angle_deg = -rate_limit * elapsed;
    }
  }
  else {
    angle_deg = angle_error * elapsed;
  }
  // convert from degrees to radians
  angle_rad = m_util.deg_to_rad(angle_deg);
  // returning array with first element angle_rad to apply to
  // m_trans.rotate_?_local command
  // And returning new cur as second element
  cur = cur + angle_deg;
  var result = [angle_rad,cur];
  return(result);
}

function tower_cb(obj, id) {
  var elapsed = m_controls.get_sensor_value(obj, id, 0);
  //cmd_yaw = 180;  // Debug
  result = cntrl(cmd_yaw,cur_yaw,elapsed,tower_ang_rate_limit_per_second);
  angle_rad = result[0];
  cur_yaw = result[1];

  // -angle_rad so that the turbine turns the correct direction
  m_trans.rotate_z_local(obj, -angle_rad);
  // Update UI
  $("#cmd_yaw").html(cmd_yaw.toFixed(2));
  $("#cur_yaw").html(cur_yaw.toFixed(2));
}

function blades_cb(obj, id) {
  // Update all the blade pitches as one
  var elapsed = m_controls.get_sensor_value(obj, id, 0);
  result = cntrl(cmd_pitch,cur_pitch,elapsed,blade_ang_rate_limit_per_second);
  angle_rad = result[0];
  cur_pitch = result[1];
  m_trans.rotate_z_local(blades[0], angle_rad);
  m_trans.rotate_z_local(blades[1], angle_rad);
  m_trans.rotate_z_local(blades[2], angle_rad);
  // Update UI
  $("#cmd_pitch").html(cmd_pitch.toFixed(2));
  $("#cur_pitch").html(cur_pitch.toFixed(2));
}

function loaded_cb() {
  m_app.enable_camera_controls();

  // Find Objects
  var rotorhub = m_scenes.get_object_by_name("ROTORHUB");
  var tower = m_scenes.get_object_by_name("tower");
  var blade1 = m_scenes.get_object_by_name("blade1");
  var blade2 = m_scenes.get_object_by_name("blade2");
  var blade3 = m_scenes.get_object_by_name("blade3");
  // Doing this so all three can be updated as one (Hack)
  blades[0] = blade1;
  blades[1] = blade2;
  blades[2] = blade3;

  //create sensor
  var elapsed_sensor = m_controls.create_elapsed_sensor();
  m_controls.create_sensor_manifold(rotorhub, "ROTORHUB", m_controls.CT_CONTINUOUS, [elapsed_sensor], null, rotorhub_cb);
  m_controls.create_sensor_manifold(tower, "TOWER", m_controls.CT_CONTINUOUS, [elapsed_sensor], null, tower_cb);
  m_controls.create_sensor_manifold(blade1, "BLADE1", m_controls.CT_CONTINUOUS, [elapsed_sensor],null, blades_cb);
  // Setup connection to web server
  setup_websocket();
}

function setup_websocket(){
  var host = "ws://" + location.host + "/wt_socket";
  socket = new WebSocket(host);
  // console.log("socket status: " + socket.readyState);
  // event handlers for websocket
  if(socket){
    socket.onopen = function(){
        //alert("connection opened....");
    }
    socket.onmessage = function(msg){
      robj = JSON.parse(msg.data);
      // Process object sent from webserver
      // Weather measurements
      if ('wind_dir' in robj){
        wind_dir = robj.wind_dir;
        //$("#wind_dir_mod").val(wind_dir.toFixed(2));
        weather_addpoint(1,wind_dir);
      }
      if ('wind_speed' in robj){
        wind_speed = robj.wind_speed;
        //$("#wind_speed_mod").val(wind_speed.toFixed(2));
        weather_addpoint(2,wind_speed);
      }
      if ('air_density' in robj){
        air_density = robj.air_density;
        //$("#air_density_mod").val(air_density.toFixed(2));
        weather_addpoint(0,air_density);
      }
      // Wind turbine controls
      if ('yaw' in robj){
        cmd_yaw = robj.yaw;
        control_addpoint(0, cmd_yaw);
      }
      if ('pitch' in robj){
        cmd_pitch = robj.pitch;
        control_addpoint(1, cmd_pitch);
      }
      // Outputs from system
      if ('power' in robj){
        power = robj.power;
        if (power < 0.1) {
          power = 0.1;
        }
        output_addpoint(0, power);
        $("#power").html(power.toFixed(2));
      }
      if ('rpm' in robj){
        cmd_rpm = robj.rpm;
        output_addpoint(1, cmd_rpm);
      }
      // Other elements
      if ('control_msg' in robj){
        message = robj.control_msg;
        message = message.replace(/(?:\r\n|\r|\n)/g, '<br />');
        $('#control_msg').append(message);
      }

    }
    socket.onclose = function(){
        //alert("connection closed....");
    }
  } else {
      console.log("invalid socket");
  }
}
