rule([ temperature(very_low) ] , do(fix_temperature(very_low,'temperature(low)'))).
rule([ temperature(very_low) ] , fact(temperature(very_high))).
rule([ temperature(low), outdoor_temperature(medium) ] , do(fix_temperature(low,'temperature(medium)'))).
rule([ temperature(low), outdoor_temperature(very_low) ] , do(fix_temperature(low,'temperature(medium)'))).
rule([ temperature(high), outdoor_temperature(medium) ] , do(fix_temperature(high,'temperature(medium)'))).
rule([ temperature(high), outdoor_temperature(very_high) ] , do(fix_temperature(high,'temperature(medium)'))).
rule([ temperature(very_high) ] , do(fix_temperature(very_high,'temperature(high)'))).
rule([ light(low), outdoor_light(medium) ] , do(fix_light(low,'light(medium)'))).
rule([ light(low), outdoor_light(low) ] , do(fix_light(low,'light(medium)'))).
rule([ light(medium), outdoor_light(low) ] , do(fix_light(mediumL,'light(high)'))).
rule([ light(medium), outdoor_light(high) ] , do(fix_light(mediumH,'light(low)'))).
rule([ light(high), outdoor_light(high) ] , do(fix_light(high,'light(medium)'))).
rule([ light(high), outdoor_light(medium) ] , do(fix_light(high,'light(medium)'))).
