rule( (actionTemperature(A) :-  bad_temperature(T), fix_temperature(T,A)) , 100 ).
rule( (actionLight(A) :-  bad_light(L), fix_light(L,A)) , 100 ).
rule( (action(A) :-  actionLight(A)) , 100 ).
rule( (action(A) :-  actionTemperature(A)) , 100 ).
rule( (bad_temperature(very_low) :-  temperature(very_low)) , 100 ).
rule( (bad_temperature(low) :-  temperature(low), outdoor_temperature(medium)) , 100 ).
rule( (bad_temperature(low) :-  temperature(low), outdoor_temperature(very_low)) , 100 ).
rule( (bad_temperature(high) :-  temperature(high), outdoor_temperature(medium)) , 100 ).
rule( (bad_temperature(high) :-  temperature(high), outdoor_temperature(very_high)) , 100 ).
rule( (bad_temperature(very_high) :-  temperature(very_high)) , 100 ).
rule( (bad_light(low) :-  light(low), outdoor_light(medium)) , 100 ).
rule( (bad_light(low) :-  light(low), outdoor_light(low)) , 100 ).
rule( (bad_light(mediumL) :-  light(medium), outdoor_light(low)) , 100 ).
rule( (bad_light(mediumH) :-  light(medium), outdoor_light(high)) , 100 ).
rule( (bad_light(high) :-  light(high), outdoor_light(high)) , 100 ).
rule( (bad_light(high) :-  light(high), outdoor_light(medium)) , 100 ).
rule( fix_temperature(very_low,'temperature(low)') , 100 ).
rule( fix_temperature(low,'temperature(medium)') , 100 ).
rule( fix_temperature(high,'temperature(medium)') , 100 ).
rule( fix_temperature(very_high,'temperature(high)') , 100 ).
rule( fix_light(low,'light(medium)') , 100 ).
rule( fix_light(mediumL,'light(high)') , 100 ).
rule( fix_light(high,'light(medium)') , 100 ).
rule( fix_light(mediumH,'light(low)') , 100 ).
askable( temperature(T) ).
askable( outdoor_temperature(T) ).
askable( light(L) ).
askable( outdoor_light(L) ).
