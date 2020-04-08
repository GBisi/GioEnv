rule([ temperature(very_low) ] , [ set_temperature(high) ]).
rule([ temperature(low), outdoor_temperature(very_low) ] , [ set_temperature(high) ]).
rule([ temperature(high), outdoor_temperature(very_high) ] , [ set_temperature(low) ]).
rule([ temperature(very_high) ] , [ set_temperature(low) ]).
rule([ light(low), outdoor_light(medium) ] , [ set_light(medium) ]).
rule([ light(low), outdoor_light(low) ] , [ set_light(high) ]).
rule([ light(medium), outdoor_light(low) ] , [ set_light(high) ]).
rule([ light(medium), outdoor_light(high) ] , [ set_light(medium) ]).
rule([ light(high), outdoor_light(high) ] , [ set_light(medium) ]).
rule([ light(high), outdoor_light(medium) ] , [ set_light(medium) ]).
