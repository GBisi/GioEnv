rule([ temperature(very_low) ] , [ do(set_temperature(high)) ]).
rule([ temperature(low), outdoor_temperature(very_low) ] , [ do(set_temperature(high)) ]).
rule([ temperature(high), outdoor_temperature(very_high) ] , [ do(set_temperature(low)) ]).
rule([ temperature(very_high) ] , [ do(set_temperature(low)) ]).
rule([ light(low), outdoor_light(medium) ] , [ do(set_light(medium)) ]).
rule([ light(low), outdoor_light(low) ] , [ do(set_light(high)) ]).
rule([ light(medium), outdoor_light(low) ] , [ do(set_light(high)) ]).
rule([ light(medium), outdoor_light(high) ] , [ do(set_light(medium)) ]).
rule([ light(high), outdoor_light(high) ] , [ do(set_light(medium)) ]).
rule([ light(high), outdoor_light(medium) ] , [ do(set_light(medium)) ]).
