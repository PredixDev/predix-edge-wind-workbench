# Edge Wind Turbine Workbench APIs
There are ____ pieces that make up the workbench.

### Weather Simulation
Results of the internally randomly generated weather measurements are available on a channel called `weather` which publishes an output object, at one second intervals, fields/members are:
* `wind_speed` - floating point value that ranges from 0-23 meters/second that indicates the wind's speed at the wind turbines location.
* `wind_dir`- floating point value that ranges from 0-360 degrees that indicates what direction the wind is coming from at the wind turbines location.
* `air_density` - floating point value that ranges from 1.12 -1.552 kilograms/meter cubed that indicates the density of the air at the turbines location.

Here is an example in python of subscribing and reading the values of a measurement.

```python
# Toy example of subscribing to the weather channel and getting a measurement using the edgeworker runtime
class MyWorker(Worker):
    def initialization(self):
        self.add_subscription('weather') # Add this to initialization to get the weather channel

    def work(self,channel,in_object):
        # When a weather measurement is published elsewhere should receive is here
        if ('weather' == channel):
            # get values from in_object
            wind_speed = in_object['wind_speed']
            wind_dir = in_object['wind_dir']
            air_density = in_object['air_density']
            # Do something with these values
""" Main and worker monitor cut out for brevity"""
```

### Turbine Control Inputs
In the simplified model of a wind turbine there are some controls that you can send information to control the wind turbine model and the 3D visualization. The turbine control is listening for inputs on channel `turbine_control` and is expecting an object with these fields/members:
* `yaw` - A floating point number indicating the direction the wind turbine is pointing to (into the wind). The value is in degrees and can be any positive or negative number (it is internally adjusted).
* `pitch` - A floating point number indicating the pitch of the turbines blades (Don't expect the 3D model to be accurate). The value is in degrees and should be in the range of -5 to 6 degrees (internally clamped).

Here is an example of commanding `yaw` and `pitch` in C#.

```cs
// Toy example of publishing to turbine_control. In this case just once during initialization
  public class WT_Control
  {
    public double yaw { get; set; }
    public double pitch { get; set; }
  }

  class MyCSharpWorker : Edgeworker.Edgeworker
  {
    WT_Control wt_object = new WT_Control;
    public override void initialization()
    {
      wt_object.yaw = 15.555;
      wt_object.pitch = 3.3;
      this.publish("turbine_control", wt_object);
    }
    public override void work(string channel, string in_object)
    {
      // Not doing anything here right now ...
    }
  }
/* Main and worker monitor cut out for brevity */
```
Note: If this code works that would be great:)

Note: The 3D model has a rate limit placed on the movement `yaw` and `pitch` movement and if this was at all meant to be realistic this would be taken into consideration in the model. It isn't currently (next revision maybe).

### Turbine Outputs
The model of the wind turbine calculates to values given the weather information and the turbine control inputs and these are available on the `turbine_measurement` channel where it provides an object with these fields/members:
* `power` - A floating point number that indicates what the model has calculated the turbine would have produced in Watts.
* `rpm` - A floating point number that indicates how fast the wind turbines model has calculated the blades are turning in RPM.

Here is an example of read `power` and `rpm` in C#.

```cs
// Toy example of subscribing and receiving  turbine_measurement.
  class MyCSharpWorker : Edgeworker.Edgeworker
  {
    public override void initialization()
    {
      this.subscribe("turbine_measurement");
    }
    public override void work(string channel, string in_object)
    {
      // Receive and deserialize
      if (channel == "turbine_measurement"){
        var turbine_m_obj = JObject.Parse(in_object);
        var power = turbine_m_obj['power'];
        var rpm = turbine_m_obj['rpm'];
        // do something wonderful now ...
      }
    }
  }
/* Main and worker monitor cut out for brevity */
```

### Web Interface
The web interface of the work bench has some inputs and outputs that are available. Some of the outputs from the Web interface are used to modify the weather simulation and others are available to your application as if they were controls in a deployed system.

#### From UI
The objects from the UI are unique in that they have a fixed set of fields/members but not all of these fields/members are transmitted all the time. In fact if they aren't changing they don't get included in the sent object also there is no fixed rate for these values. Many of the other interfaces will produce data at a 1 second interval for the `from_ui` channel the message is not published unless something changes (a human interacts with the UI).  The example below shows how to deal with this in Python. The fields/members include:
* `param_a` - `param_f` - On the front panel of the Edge Wind Turbine Workbench there are 6 numeric entry form fields that can be used for anything you want. They are time based in that one second after you stop entering a number in the field they publish their value.
* `toggle_1_btn` - `toggle_6_btn` - On the front panel of the Edge Wind Turbine Workbench there are 6 push buttons that can be toggled from true to false by successive clicks on the button. These publish either a `true` or `false` value.
* `wind_speed_mod`, `wind_dir_mod` and `air_density_mod` - These values come from the UI but are intended for the Weather Simulation. They will set the current value of the Random Walk object to that value and then will allow the random walk to continue. They aren't intended for the use of those writing apps but 'what the hay':) Besides you might see them.

Here is an example in python of subscribing and reading the values from the UI. Remember not all of the fields will be there.

```python
# Toy example of subscribing to the weather channel and getting a measurement using the edgeworker runtime
class MyWorker(Worker):
    def initialization(self):
        self.add_subscription('from_ui') # Add this to initialization to get the weather channel
        self.local_value_a = 5.0
        self.list_b = []  # keeps the last 10 values seen

    def work(self,channel,in_object):
        # When a weather measurement is published elsewhere should receive is here
        if ('from_ui' == channel):
            # get values from in_object

            # Example just update a value when needed
            # object.get(field, default_value_if_field_not_present)
            self.local_value_a = in_object.get('param_a', self.local_value_a)

            # Example get value if it exists and do some processing
            if 'param_b' in in_object:
                value = in_object['param_b']
                self.list_b.append(value)
                self.list_b = self.list_b[-10:]

            if 'toggle_1_btn' in in_object and in_object['toggle_1_btn']:
                # Called when present and True
                # clear list_b
                self.list_b = []

""" Main and worker monitor cut out for brevity"""
```
#### To UI
Most of the data going to the UI comes from the Weather and Wind Turbine simulations but there is some data that the app developer can send via the `to_ui` channel.
* `control_msg` - Is a string or multiline (linefeed) string that will be displayed in the 'Other output from App' panel within the UI. Anything that you can be convert to string you can have displayed here.
