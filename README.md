ISS Notification
---------------- 

Display upcoming passes of the International Space Station using the
open source OpenNotify API at http://api.open-notify.org. Optionally,
output status information over a serial port for physical notifications

Requirements
------------

- python-requests
- python-serial
- python-enum34

Explanation
-----------

Uses the open source API at http://api.open-notify.org to retrieve calculated
overhead passes of the International Space Station for a given longitude and
latitude pair.

Retrieved passes get printed to the screen and optionally simple status codes can
be sent over a serial port specified by -s (or --serial). This is intended to be
used in order to send some physical indication of future ISS passes, i.e. light an
LED etc

The script uses a series of simple states, which depending on how far away the ISS
is from the invokers location dictates how often pass data is retrieved. These 
states are defined in the dictionary object iss_states but can be described as 
follows:

- RECEDING 	(more than 45 minutes away, updates every 120s)
- APPROACHING   	(less than 45 minutes, but more than 15 minutes away, updates every 60s)
- CLOSING		(less than 15 minutes, but more than 5 minutes away, updates every 30s)
- INCOMING	(less than 5 minutes, updates every 15s)
- IMMINENT	(less than 1 minute, updates every 5s)
- OVERHEAD	(less than 0 seconds, updates after the estimated pass duration)

This scheme is used in order to minimise load on the open-notify API servers whilst 
attempting to increase the acccuracy of notifications as the ISS approaches.

If using the --serial option, different codes are sent (currently simple ascii values) 
according to 'state' transitions (see above) as the state machine advances through the
various stages of the ISS' orbital path.

Currently, the script outputs commands as the letters A thru F, with Z being used as a
test command. Commands are delimited by a lead '$' and a trailing '!'  

OpenNotify is copyright of Nathan Bergey (@natronics). I take no responsibility for any 
inaccuracies that may arise from using this data provided by the service. 

See http://open-notify.org for further information on the OpenNotify API

I also take no responsibility for any inaccuracies that may arise from outputs of this 
script. Notifications are only accurate to within a few seconds and are not intended to 
give scientifically precise indications of the ISS' orbital path. They are purely provided
for casual observation of ISS passes.

Invocation
----------

The only required paramters are a latitude/longitude pair, so the script can simply be
invoked as follows to display pass data to the console:

- python ./iss_notitification.py --latitude 33.51 --longitude -78.53

Often, the screen utility is useful to start the process in a background window, like the
following example (good for startup scripts):

- screen -d -m -S "ISS_NOTIFY" python ./iss_notification.py --latitude 33.51 --longitude -78.53
 --passes 1 --altitude 10 --serial /dev/ttyUSB0

More detailed usage information can be found by invoking the scripts built in usage 
documentation as follows:

- python ./iss_notification.py --help

Tested on python version 2.7.5

- Happy Observing

License & Copyright
-------------------

Copyright (C) 2014 - Zerosignal (zerosignal1982@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

The OpenNotify API is copyright Nathan Bergey (@natronics)
