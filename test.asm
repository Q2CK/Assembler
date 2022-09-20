#isa AnPU2
#define bajo 3
#define jajo 4

lim $0, 0
lim $1, 1
.loop
lda $0
add $1
sta $0
add $1
sta $1
bno loop
add jajo
