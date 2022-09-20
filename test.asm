#isa AnPU2
#define bajo 2
#define jajo 4

lim $0, 0
lim $1, 1
//costam
.loop
lda $0
add $1
sta $0
add $1
sta $1
bno loop
add bajo
