import string
from enum import Enum
from .nimlexbase import TBaseLexer

# constants
max_line_len = 80
num_chars = list(
    [c for c in string.digits]
    + [c for c in string.ascii_uppercase]
    + [c for c in string.ascii_lowercase]
)
sym_chars = num_chars + [hex(h) for h in range(128, 256)]
sym_start_chars = list(
    [c for c in string.ascii_uppercase]
    + [c for c in string.ascii_lowercase]
    + [hex(h) for h in range(128, 256)]
)

TTokType = Enum("TTokType", [
    "tkInvalid", "tkEof",               # order is important here!
    "tkSymbol",  # keywords:
    "tkAddr", "tkAnd", "tkAs", "tkAsm",
    "tkBind", "tkBlock", "tkBreak", "tkCase", "tkCast",
    "tkConcept", "tkConst", "tkContinue", "tkConverter",
    "tkDefer", "tkDiscard", "tkDistinct", "tkDiv", "tkDo",
    "tkElif", "tkElse", "tkEnd", "tkEnum", "tkExcept", "tkExport",
    "tkFinally", "tkFor", "tkFrom", "tkFunc",
    "tkIf", "tkImport", "tkIn", "tkInclude", "tkInterface",
    "tkIs", "tkIsnot", "tkIterator",
    "tkLet",
    "tkMacro", "tkMethod", "tkMixin", "tkMod", "tkNil", "tkNot", "tkNotin",
    "tkObject", "tkOf", "tkOr", "tkOut",
    "tkProc", "tkPtr", "tkRaise", "tkRef", "tkReturn",
    "tkShl", "tkShr", "tkStatic",
    "tkTemplate",
    "tkTry", "tkTuple", "tkType", "tkUsing",
    "tkVar", "tkWhen", "tkWhile", "tkXor",
    "tkYield",  # end of keywords
    "tkIntLit", "tkInt8Lit", "tkInt16Lit", "tkInt32Lit", "tkInt64Lit",
    "tkUIntLit", "tkUInt8Lit", "tkUInt16Lit", "tkUInt32Lit", "tkUInt64Lit",
    "tkFloatLit", "tkFloat32Lit", "tkFloat64Lit", "tkFloat128Lit",
    "tkStrLit", "tkRStrLit", "tkTripleStrLit",
    "tkGStrLit", "tkGTripleStrLit", "tkCharLit", "tkParLe", "tkParRi", "tkBracketLe",
    "tkBracketRi", "tkCurlyLe", "tkCurlyRi",
    "tkBracketDotLe", "tkBracketDotRi",  # [. and .]
    "tkCurlyDotLe", "tkCurlyDotRi",  # {. and .}
    "tkParDotLe", "tkParDotRi",  # (. and .)
    "tkComma", "tkSemiColon",
    "tkColon", "tkColonColon", "tkEquals", "tkDot", "tkDotDot", "tkBracketLeColon",
    "tkOpr", "tkComment", "tkAccent",
    "tkSpaces", "tkInfixOpr", "tkPrefixOpr", "tkPostfixOpr"
])

TTokTypes = set(TTokType)

weakTokens = set([TTokType.tkComma, TTokType.tkSemiColon, TTokType.tkColon,
                  TTokType.tkParRi, TTokType.tkParDotRi, TTokType.tkBracketRi, TTokType.tkBracketDotRi,
                  TTokType.tkCurlyRi])

tokKeywordLow = TTokType(TTokType.tkSymbol.value + 1)
tokKeywordHigh = TTokType(TTokType.tkIntLit.value - 1)

TokTypeToStr = [
    "tkInvalid", "[EOF]",
    "tkSymbol",
    "addr", "and", "as", "asm",
    "bind", "block", "break", "case", "cast",
    "concept", "const", "continue", "converter",
    "defer", "discard", "distinct", "div", "do",
    "elif", "else", "end", "enum", "except", "export",
    "finally", "for", "from", "func", "if",
    "import", "in", "include", "interface", "is", "isnot", "iterator",
    "let",
    "macro", "method", "mixin", "mod",
    "nil", "not", "notin", "object", "of", "or",
    "out", "proc", "ptr", "raise", "ref", "return",
    "shl", "shr", "static",
    "template",
    "try", "tuple", "type", "using",
    "var", "when", "while", "xor",
    "yield",
    "tkIntLit", "tkInt8Lit", "tkInt16Lit", "tkInt32Lit", "tkInt64Lit",
    "tkUIntLit", "tkUInt8Lit", "tkUInt16Lit", "tkUInt32Lit", "tkUInt64Lit",
    "tkFloatLit", "tkFloat32Lit", "tkFloat64Lit", "tkFloat128Lit",
    "tkStrLit", "tkRStrLit",
    "tkTripleStrLit", "tkGStrLit", "tkGTripleStrLit", "tkCharLit", "(",
    ")", "[", "]", "{", "}", "[.", ".]", "{.", ".}", "(.", ".)",
    ",", ";",
    ":", "::", "=", ".", "..", "[:",
    "tkOpr", "tkComment", "`",
    "tkSpaces", "tkInfixOpr",
    "tkPrefixOpr", "tkPostfixOpr"
]

TNumericalBase = Enum("TNumericalBase", [
    "base10", # base10 is the first element so that it is the correct default value
    "base2", "base8", "base16"
])

CursorPosition = Enum("CursorPosition", [
    "None", "InToken", "BeforeToken", "AfterToken"
])

class TToken:
    def __init__(self):
        self.tokType = None
        self.indent = None
        self.ident = None
        self.iNumber = None
        self.fNumber = None
        self.base = None
        self.strongSpaceA = None
        self.strongSpaceB = None
        self.literal = None
        self.line = None
        self.col = None

    def initToken(self):
        self.tokType = TTokType.tkInvalid
        self.iNumber = 0
        self.indent = 0
        self.strongSpaceA = 0
        self.literal = ""
        self.fNumber = 0.0
        self.base = TNumericalBase.base10
        self.ident = None

    def fillToken(self):
        self.tokType = TTokType.tkInvalid
        self.iNumber = 0
        self.indent = 0
        self.strongSpaceA = 0
        self.literal = ""
        self.fNumber = 0.0
        self.base = TNumericalBase.base10
        self.ident = None


class TLexer(TBaseLexer):
    def __init__(self):
        self.fileIdx = None         # TODO : impl FileIndex
        self.indentAhead: int = None
        self.currLineIndent: int = None
        self.strongSpaces: bool = None
        self.allowTabs: bool = None
        self.cursor: CursorPosition = None
        self.errorHandler = None    # TODO : impl TErrorHandler
        self.cache = None           # TODO : impl IdentCache
        self.config = None          # TODO : impl ConfigRef

    def getLineInfo(self, tok:TToken):
        # TODO : impl `msgs.newLineInfo`
        # result = newLineInfo(self.fileIdx, tok.line, tok.col)
        # return result
        pass

    def openLexer(self, fileIdx, inputstream, cache, config):
        self.openBaseLexer(inputstream)
        self.fileIdx = fileIdx
        self.indentAhead = -1
        self.currLineIndent - 0
        self.lineNumber += inputstream.lineOffset
        self.cache = cache
        self.config = config
    
    def closeLexer(self):
        if self.config is not None:
            self.config.linesCompiled += self.lineNumber
        self.closeBaseLexer()

    def dispMessage(self, info, msg, arg):
        if self.errorHandler.isNil:
            # TODO : impl `msgs.message`
            # msgs.message(self.config, info, msg, arg)
            pass
        else:
            # TODO :  impl `TErrorHandler`
            # self.errorHandler(self.config, info, msg, arg)
            pass

    def lexMessage(self, msg, arg=""):
        self.dispMessage(self.getLineInfo(), msg, arg)

    

