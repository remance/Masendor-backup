Animation

the file need to be in this format:
direction name, filename, base position x, base position y, angle, flip (0=none,1=hori,2=verti,3=both), layer, scale (1 for default)

The position is based on the default side before any flip (face right for side, corner up and corner down).

layer value is similar to pygame layer, the higher value get drew first and lower value get drew later and above the higher value layer. Layer must start from 1 and should not have duplcate value, layer 0 will not be drew.

List of animation frame properties:
"hold": frame can be hold with input
"turret": not sure how it will work yet but for when sprite can face other direction while walking in other direction 
"effect_": add special image effect (not animation effect) like blur, need effect name after and related input value "effect_" (e.g., effect_blur_50)

List of animation effect propertiers:  # only need to be put in at the first frame row.  
"interuptrevert": effect run revert back to first frame when animation is interupted, can only be use with external effect
"wholeeffect_": add special image effect to every sprite, need effect name after and related input value "wholeeffect_" (e.g., wholeeffect_blur_50)