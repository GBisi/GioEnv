rule([ temperature(very_low) ] , do(set_temperature(low))).
rule([ temperature(low), outdoor_temperature(medium) ] , do(set_temperature(medium))).
rule([ temperature(low), outdoor_temperature(low) ] , do(set_temperature(medium))).
rule([ temperature(low), outdoor_temperature(very_low) ] , do(set_temperature(medium))).
rule([ temperature(high), outdoor_temperature(medium) ] , do(set_temperature(medium))).
rule([ temperature(high), outdoor_temperature(high) ] , do(set_temperature(medium))).
rule([ temperature(high), outdoor_temperature(very_high) ] , do(set_temperature(medium))).
rule([ temperature(very_high) ] , do(set_temperature(high))).
rule([ light(low), outdoor_light(medium) ] , do(set_light(medium))).
rule([ light(low), outdoor_light(low) ] , do(set_light(medium))).
rule([ light(medium), outdoor_light(low) ] , do(set_light(high))).
rule([ light(medium), outdoor_light(high) ] , do(set_light(low))).
rule([ light(high), outdoor_light(high) ] , do(set_light(medium))).
rule([ light(high), outdoor_light(medium) ] , do(set_light(medium))).
