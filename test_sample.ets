//! CHECKER       AOT IR Builder, check String concatenation loop
//! SKIP_IF       @architecture == "arm32"
//! RUN           entry: "ets_string_concat_loop.ETSGLOBAL::main"

//! METHOD        "ets_string_concat_loop.ETSGLOBAL::concat_loop0"
//! PASS_BEFORE   "BranchElimination"
//! IN_BLOCK      /loop/
//! INST          /StringBuilder::<ctor>/
//! INST_COUNT    /Intrinsic.StdCoreSbAppendString/,2
//! INST          /Intrinsic.StdCoreSbToString/
//! PASS_AFTER    "SimplifyStringBuilder"
//! IN_BLOCK      /prehead/
//! INST          /StringBuilder::<ctor>/
//! INST          /Intrinsic.StdCoreSbAppendString/
//! PASS_AFTER    "SimplifyStringBuilder"
//! IN_BLOCK      /loop/
//! INST          /Intrinsic.StdCoreSbAppendString/
//! INST_NOT      /Intrinsic.StdCoreSbToString/
//! PASS_AFTER    "SimplifyStringBuilder"
//! INST          /Intrinsic.StdCoreSbToString/

//! METHOD        "ets_string_concat_loop.ETSGLOBAL::concat_loop5"
//! PASS_BEFORE   "BranchElimination"
//! IN_BLOCK      /loop/
//! INST_COUNT    /StringBuilder::<ctor>/,2
//! INST_COUNT    /Intrinsic.StdCoreSbAppendString/,4
//! INST_COUNT    /Intrinsic.StdCoreSbToString/,2
//! PASS_AFTER    "ChecksElimination"
//! IN_BLOCK      /prehead/
//! INST_COUNT    /StringBuilder::<ctor>/,1
//! INST_COUNT    /Intrinsic.StdCoreSbAppendString/,1
//! PASS_AFTER    "ChecksElimination"
//! IN_BLOCK      /loop/
//! INST_COUNT    /Intrinsic.StdCoreSbAppendString2/,1
//! INST_NOT      /Intrinsic.StdCoreSbToString/
//! PASS_AFTER    "ChecksElimination"
//! INST_COUNT    /Intrinsic.StdCoreSbToString/,1

function concat_loop0(a: String, n: int): String {
    let str: String = "";
    for (let i = 0; i < n; ++i)
        str = str + a;
    return str;
}

function concat_loop5(strings: FixedArray<string>): String {
    let str: String = "";
    for (let i = 0; i < strings.length; ++i) {
        str += strings[0] + strings[i];
    }
    return str;
}

function main() {
    assertEQ(concat_loop0("a", 4), "aaaa", "Wrong result at concat_loop0");
    assertEQ(concat_loop5(["a", "b", "c", "d"]), "aaabacad", "Wrong result at concat_loop5");
} 