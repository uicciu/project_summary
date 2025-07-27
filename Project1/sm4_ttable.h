#ifndef SM4_TTABLE_H
#define SM4_TTABLE_H

#include "sm4.h"

class SM4_TTable : public SM4 {
public:
    SM4_TTable();
protected:
    uint32_t T(uint32_t x) override;

private:
    static uint32_t T0[256], T1[256], T2[256], T3[256];
    static void initTtables();
};

#endif // SM4_TTABLE_H
