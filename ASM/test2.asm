#isa AnPUNano

//fibonacci

imm $0, 0, 123456
imm $1, 1
.loop
add $0, $0, $1
add $1, $0, $1
jmp loop
