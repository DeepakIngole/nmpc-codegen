#ifndef LBFGS_H
#define LBFGS_H

#include "../globals/globals.h"
#include <stddef.h>
#include <stdlib.h>

int lbfgs_init(const size_t buffer_size_,const size_t dimension_, \
    int (*gradient_)(const real_t* input,real_t* output));
int lbfgs_cleanup(void);

/*
 * returns the direction calculated with lbfgs
 */ 
 int lbfgs_get_direction(const real_t* current_location,real_t* direction);

#endif 