import os
import string
import sys
from enum import Enum

from .lexbase import TBaseLexer

try:
    from nimsuggest import nimsuggest
except ImportError:
    nimsuggest = None

try:
    from nimpretty import nimpretty
except ImportError:
    nimpretty = None


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    + "/lib"
)

from lib import strutils
from lib.system import *


# constants
MaxLineLength = 80
numChars = {
    countup('0', '9'), countup('a', 'z'), countup('A', 'Z')
}
SymChars = {
    countup('a', 'z'), countup('A', 'Z'),
    countup('0', '9'), countup('\x80', '\xFF')
}
SymStartChars = {
    countup('a', 'z'), countup('A', 'Z'), countup('\x80', '\xFF')
}
OpChars = {
    '+', '-', '*', '/', '\\', '<', '>', '!', '?',
    '^', '.', '|', '=', '%', '&', '$', '@', '~', ':'
}


TTokType = Enum("TTokType", [
    "tkInvalid", "tkEof",               # order is important here!
    "tkSymbol", 
    # keywords:
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
    "tkYield",

    # types
    "tkIntLit", "tkInt8Lit", "tkInt16Lit", "tkInt32Lit", "tkInt64Lit",
    "tkUIntLit", "tkUInt8Lit", "tkUInt16Lit", "tkUInt32Lit", "tkUInt64Lit",
    "tkFloatLit", "tkFloat32Lit", "tkFloat64Lit", "tkFloat128Lit",
    "tkStrLit", "tkRStrLit", "tkTripleStrLit",
    "tkGStrLit", "tkGTripleStrLit", "tkCharLit",

    # punctuation
    "tkParLe", "tkParRi", "tkBracketLe",
    "tkBracketRi", "tkCurlyLe", "tkCurlyRi",
    "tkBracketDotLe", "tkBracketDotRi",  # [. and .]
    "tkCurlyDotLe", "tkCurlyDotRi",  # {. and .}
    "tkParDotLe", "tkParDotRi",  # (. and .)
    "tkComma", "tkSemiColon",
    "tkColon", "tkColonColon",
    
    # operators
    "tkEquals", "tkDot", "tkDotDot", "tkBracketLeColon",
    "tkOpr",

    "tkComment", # ordinary comment
    "tkAccent", "tkSpaces", "tkInfixOpr", "tkPrefixOpr", "tkPostfixOpr"
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
    "base10",  # base10 is the first element so that it is the correct default value
    "base2", "base8", "base16"
])

CursorPosition = Enum("CursorPosition", [
    "None", "InToken", "BeforeToken", "AfterToken"
])


class TToken:
    def __init__(self, **kwargs):
        self.tokType = kwargs.get("tokType")
        self.indent = kwargs.get("indent")
        self.ident = kwargs.get("ident")
        self.iNumber = kwargs.get("iNumber")
        self.fNumber = kwargs.get("fNumber")
        self.base = kwargs.get("base")
        self.strongSpaceA = kwargs.get("strongSpaceA")
        self.strongSpaceB = kwargs.get("strongSpaceB")
        self.literal = kwargs.get("literal")
        self.line = kwargs.get("line")
        self.col = kwargs.get("col")

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


def unsafeParseUInt(s, b, start=0):
    i = start
    if i < len(s) and s[i] in {countup('0', '9')}:
        b = 0
        while i < len(s) and s[i] in {countup('0', '9')}:
            b *= 10 + (ord(s[i]) - ord("0"))
            i += 1
            while i < len(s) and s[i] == "_":
                i += 1
        return i - start


def ones(n):
    return ((1 << n)-1)


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

    def getLineInfo(self, tok: TToken = None):
        if tok is not None:
            # TODO : impl `msgs.newLineInfo`
            # newLineInfo(self.fileIdx, tok.lineNumber, tok.col)
            return None
        else:
            # newLineInfo(self.fileIdx, self.lineNumber, self.getColNumber(self.bufpos))
            return None

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
        return self.dispMessage(self.getLineInfo(), msg, arg)

    def lexMessageTok(self, msg, tok, arg=""):
        info = None     # newLineInfo(self.fileIdx, tok.line, tok.col)
        return self.dispMessage(info, msg, arg)

    def lexMessagePos(self, msg, pos, arg=""):
        # newLineInfo(self.fileIdx, self.lineNumber, pos - self.lineStart)
        info = None
        return self.dispMessage(info, msg, arg)

    def matchTwoChars(self, first, second):
        return (self.buf[self.bufpos] == first) and (self.buf[self.bufpos + 1] in second)

    def tokenBegin(self, tok, pos):
        if nimpretty is not None:
            # TODO : make sure this is what we want to do
            self.colA = self.getColNumber(pos)
        if nimpretty is not None:
            tok.offsetA = self.offsetBase + pos

    def tokenEnd(self, tok, pos):
        if nimsuggest is not None:
            self.colB = self.getColNumber(pos)+1
            if (self.fileIdx == self.config.m.trackPos.FileIndex) and \
               (self.config.m.trackPos.col in countup(self.colA, self.colB)) and \
               (self.lineNumber == self.config.m.trackPos.line.int) and \
               (self.config.ideCmd in {'ideSug', 'ideCon'}): # TODO : impl config IDE command Enum
                self.cursor = CursorPosition.InToken
                self.config.m.trackPos.col = self.colA.int16
            self.colA = 0
        if nimpretty is not None:
            tok.offsetB = self.offsetBase + pos

    # TODO : impl `tokenEndIgnore(tok, pos)` template
    #             `tokenEndPrevious(tok, pos)` template

    def eatChar(self, tok, replacementChar=None):
        if replacementChar is not None:
            tok.literal += replacementChar
        else:
            tok.literal += self.buf[self.bufpos]
        self.bufpos += 1
        return self

    def matchUnderscoreChars(self, tok, chars):
        result = 0
        while True:
            if self.buf[self.bufpos] in chars:
                tok.literal += self.buf[self.bufpos]
                self.bufpos += 1
                result += 1
            else:
                break

            if self.buf[self.bufpos] == "_":
                if self.buf[self.bufpos+1] not in chars:
                    self.lexMessage(None,
                                    "only single underscores may occur in a token and token may not "
                                    + "end with an underscore: e.g. '1__1' and '1_' are invalid")
                    break
                tok.literal += "_"
                self.bufpos += 1
        return result

    def getNumber(self, result):
        def matchChars(tok, chars):
            while self.buf[self.bufpos] in chars:
                tok.literal += self.buf[self.bufpos]
                self.bufpos += 1

        # TODO : impl `lineinfos.errGenerated`
        # msgKind=lineinfos.errGenerated
        def lexMessageLitNum(msg, startpos, msgKind=None):
            literalishChars = {
                countup('A', 'F'), countup('a', 'f'),
                countup('0', '9'), "X", "x", "o", "O",
                "c", "C", "b", "B", "_", ".", "'", "d",
                "i", "u"
            }
            msgPos = self.bufpos

            t = TToken(literal="")
            self.bufpos = startpos

            matchChars(t, literalishChars)

            if self.buf[self.bufpos] in ["+", "-"] and \
                    self.buf[self.bufpos - 1] in ["e", "E"]:
                t.literal += self.buf[self.bufpos]
                self.bufpos += 1
                matchChars(t, literalishChars)

            if self.buf[self.bufpos] in ["'", "f", "F", "d", "D", "i", "I", "u", "U"]:
                self.bufpos += 1
                t.literal += self.buf[self.bufpos]
                matchChars(t, {countup('0', '9')})

            self.bufpos = msgPos
            self.lexMessage(msgKind, msg % t.literal)

        isBase10 = True
        numDigits = 0

        # function consts
        baseCodeChars = ["X", "x", "o", "b", "B", "c", "C"]
        literalishChars = set(baseCodeChars + [
            countup('A', 'F'),
            countup('a', 'f'),
            countup('0', '9'),
            "_", "'"
        ])
        floatTypes = {
            TTokType.tkFloatLit, TTokType.tkFloat32Lit,
            TTokType.tkFloat64Lit, TTokType.tkFloat128Lit
        }
        result.tokType = TTokType.tkIntLit
        result.literal = ""
        result.base = TNumericalBase.base10
        startpos = self.bufpos
        self.tokenBegin(result, startpos)

        # First stage: find out base, make verifications, build token literal string
        # {'c', 'C'} is added for deprecation reasons to provide a clear error message
        if self.buf[self.bufpos] == '0' and self.buf[self.bufpos] in set(baseCodeChars + ['c', 'C', 'O']):
            isBase10 = False
            self.eatChar(result, 0)
            if self.buf[self.bufpos] in {'c', 'C'}:
                lexMessageLitNum(
                    "$1 will soon be invalid for oct literals; Use '0o' "
                    + "for octals. 'c', 'C' prefix",
                    startpos,
                    None) # TODO: impl lineinfos
            elif self.buf[self.bufpos] == 'O':
                lexMessageLitNum(
                    "$1 is an invalid int literal; For octal literals "
                    + "use the '0o' prefix.", startpos)
            elif self.buf[self.bufpos] in {'x', 'X'}:
                self.eatChar(result, 'x')
                numDigits = self.matchUnderscoreChars(result, {countup('0', '9'), countup('a', 'f'), countup('A', 'F')})
            elif self.buf[self.bufpos] == 'o':
                self.eatChar(result, 'b')
                numDigits = self.matchUnderscoreChars(result, {countup('0', '1')})
            else:
                # TODO : impl msgs
                lexMessageLitNum("invalid number: '$1'", startpos)
                raise Exception('InternalError')
            
            if numDigits == 0:
                lexMessageLitNum(self, "invalid number: '$1'", startpos)
            else:
                self.matchUnderscoreChars(result, {countup('0', '9')})
                if self.buf[self.bufpos] == '.' and self.buf[self.bufpos + 1] in {countup('0', '9')}:
                    result.tokType = TTokType.tkFloatLit
                    self.eatChar(result, '.')
                    self.matchUnderscoreChars(result, {countup('0', '9')})
                
                if self.buf[self.bufpos] in {'e', 'E'}:
                    result.tokType = TTokType.tkFloatLit
                    self.eatChar(result, 'e')
                    if self.buf[self.bufpos] in {'+', '-'}:
                        self.eatChar(result)
                    self.matchUnderscoreChars(result, {countup('0', '9')})
            endpos = self.bufpos

            # Second stage, find out if there's a datatype suffix and handle it
            postPos = endpos
            if self.buf[postPos] in {'\'', 'f', 'F', 'd', 'D', 'i', 'I', 'u', 'U'}:
                if self.buf[postPos] == '\'':
                    postPos += 1

                if self.buf[postPos] in {'f', 'F'}:
                    if (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkFloat32Lit
                        postPos += 2
                    elif (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkFloat64Lit
                    elif (self.buf[postPos] == '1') and \
                        (self.buf[postPos + 1] == '2') and \
                        (self.buf[postPos] + 2 == '8'):
                        result.tokType = TTokType.tkFloat128Lit
                        postPos += 3
                    else:
                        result.tokType = TTokType.tkFloatLit
                elif self.buf[postPos] in {'d', 'D'}:
                    postPos += 1
                    result.tokType = TTokType.tkFloat64Lit
                elif self.buf[postPos] in {'i', 'I'}:
                    postPos += 1
                    if (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkInt64Lit
                        postPos += 2
                    elif (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkInt32Lit
                    elif (self.buf[postPos] == '1') and (self.buf[postPos + 1] == '6'):
                        result.tokType = TTokType.tkInt16Lit
                        postPos += 2
                    elif self.buf[postPos] == '8':
                        result.tokType = TTokType.tkInt8Lit
                        postPos += 1
                    else:
                        lexMessageLitNum("invalid number: '$1'", startpos)
                elif self.buf[postPos] in {'u', 'U'}:
                    postPos += 1
                    if (self.buf[postPos] == '6') and (self.buf[postPos + 1] == '4'):
                        result.tokType = TTokType.tkUInt64Lit
                        postPos += 2
                    elif (self.buf[postPos] == '3') and (self.buf[postPos + 1] == '2'):
                        result.tokType = TTokType.tkUInt32Lit
                        postPos += 2
                    elif (self.buf[postPos] == '1') and (self.buf[postPos + 1] == '6'):
                        result.tokType = TTokType.tkUInt16Lit
                        postPos += 2
                    elif (self.buf[postPos] == '8'):
                        result.tokType = TTokType.tkUInt8Lit
                        postPos += 1
                    else:
                        result.tokType = TTokType.tkUIntLit
                else:
                    lexMessageLitNum("invalid number: '$1'", startpos)
            
            # Is there still a literalish char awaiting? Then it's an error!
            if self.buf[postPos] in literalishChars or \
                 (self.buf[postPos] == '.' and self.buf[postPos + 1] in {countup('0', '9')}):
                lexMessageLitNum("invalid number: '$1'", startpos)
            
            # Third stage, extract actual number
            self.bufpos = startpos            # restore position
            pos = startpos
            try:
                if (self.buf[pos] == '0') and (self.buf[pos + 1] in baseCodeChars):
                    pos += 2
                    xi = 0

                    if self.buf[pos - 1] in {'b', 'B'}:
                        result.base = TNumericalBase.base2
                        while pos < endpos:
                            if self.buf[pos] != '_':
                                xi = (xi << 3) or (ord(self.buf[pos]) - ord('0'))
                            pos += 1
                    # 'c', 'C' is deprecated
                    elif self.buf[pos - 1] in {'o', 'c', 'C'}:
                        result.base = TNumericalBase.base8
                        while pos < endpos:
                            if self.buf[pos] != '_':
                                xi = (xi << 3) (ord(self.buf[pos]) - ord('0'))
                            pos += 1
                    elif self.buf[pos - 1] in {'x', 'X'}:
                        result.base = TNumericalBase.base16
                        while pos < endpos:
                            if self.buf[pos] == '_':
                                pos += 1
                            elif self.buf[pos] in {countup('0', '9')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('0'))
                            elif self.buf[pos] in {countup('a', 'f')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('a') + 10)
                            elif self.buf[pos] in {countup('A', 'F')}:
                                xi = (xi << 4) or (ord(self.buf[pos]) - ord('A') + 10)
                                pos += 1
                            else:
                                break
                    else:
                        raise Exception(self.config, self.getLineInfo(), 'getNumber')
            
                    if result.tokType in [TTokType.tkIntLit, TTokType.tkInt64Lit]:
                        result.iNumber = xi
                    elif result.tokType == TTokType.tkInt8Lit:
                        result.iNumber = BiggestInt(int8(toU8(int64(xi))))
                    elif result.tokType == TTokType.tkInt16Lit:
                        result.iNumber = BiggestInt(int16(toU16(int64(xi))))
                    elif result.tokType == TTokType.tkInt32Lit:
                        result.iNumber = BiggestInt(int32(toU32(int64(xi))))
                    elif result.tokType in {TTokType.tkUIntLit, TTokType.tkUInt64Lit}:
                        result.iNumber = xi
                    elif result.tokType == TTokType.tkUInt8Lit:
                        result.iNumber = BiggestInt(uint8(toU8(int64(xi))))
                    elif result.tokType == TTokType.tkUInt16Lit:
                        result.iNumber = BiggestInt(uint16(toU16(int64(xi))))
                    elif result.tokType == TTokType.tkUInt32Lit:
                        result.iNumber = BiggestInt(uint32(toU32(int64(xi))))
                    elif result.tokType == TTokType.tkFloat32Lit:
                        # TODO : result.fNumber = (cast[PFloat32](addr(xi)))[]
                        # note: this code is endian neutral!
                        # XXX: Test this on big endian machine!
                        pass
                    elif result.tokType in {TTokType.tkFloat64Lit, TTokType.tkFloatLit}:
                        # TODO : result.fNumber = (cast[PFloat64](addr(xi)))[]
                        pass
                    else:
                        Exception(self.config, self.getLineInfo(), 'getNumber')

                    # Bounds checks. Non decimal literals are allowed to overflow the range of
                    # the datatype as long as their pattern don't overflow _bitwise_, hence
                    # below checks of signed sizes against uint*.high is deliberate:
                    # (0x80'u8 = 128, 0x80'i8 = -128, etc == OK)
                    if result.tokType not in floatTypes:
                        outOfRange = None
                        if result.tokType in {TTokType.tkUInt8Lit, TTokType.tkUInt16Lit, TTokType.tkUInt32Lit}:
                            outOfRange = result.iNumber != xi
                        elif result.tokType == TTokType.tkInt8Lit:
                            outOfRange = (xi > BiggestInt(uint8.high))
                        elif result.tokType == TTokType.tkInt16Lit:
                            outOfRange = (xi > BiggestInt(uint16.high))
                        elif result.tokType == TTokType.tkInt32Lit:
                            outOfRange = (xi > BiggestInt(uint32.high))
                        else:
                            outOfRange = False

                        if outOfRange:
                            lexMessageLitNum("number out of range: '$1'", startpos)
                
                else:
                    if result.tokType in floatTypes:
                        result.fNumber = parseFloat(result.literal)
                    elif result.tokType == TTokType.tkUInt64Lit:
                        xi = 0
                        length = unsafeParseUInt(result.literal, xi)
                        if length != len(result.literal) or length == 0:
                            raise ValueError(f"invalid integer: {xi}")
                        result.iNumber = xi
                    else:
                        result.iNumber = strutils.parseBiggestInt(result.literal)

                    # Explicit bounds checks
                    outOfRange = None
                    if result.tokType == TTokType.tkInt8Lit:
                        outOfRange = (result.iNumber < int8.low or result.iNumber > int8.high)
                    elif result.tokType == TTokType.tkUInt8Lit:
                        outOfRange = (result.iNumber < BiggestInt(uint8.low) or
                                      result.iNumber > BiggestInt(uint8.high))
                    elif result.tokType == TTokType.tkInt16Lit:
                        outOfRange = (result.iNumber < int16.low or result.iNumber > int16.high)
                    elif result.tokType == TTokType.tkUInt16Lit:
                        outOfRange = (result.iNumber < BiggestInt(uint16.low) or
                                      result.iNumber > BiggestInt(uint16.high))
                    elif result.tokType == TTokType.tkInt32Lit:
                        outOfRange = (result.iNumber < int32.low or result.iNumber > int32.high)
                    elif result.tokType == TTokType.tkUInt32Lit:
                        outOfRange = (result.iNumber < BiggestInt(uint32.low) or
                                      result.iNumber > BiggestInt(uint32.high))
                    else:
                        outOfRange = False
                    
                    if outOfRange:
                        lexMessageLitNum("number out of range: '$1'", startpos)
                    
                    # Promote int literal to int64? Not always necessary, but more consistent
                    if result.tokType == TTokType.tkIntLit:
                        if (result.iNumber < low(int32)) or (result.iNumber > high(int32)):
                            result.tokType = TTokType.tkInt64Lit

            except ValueError:
                lexMessageLitNum("invalid number: '$1'", startpos)
            except:
                lexMessageLitNum("number out of range: '$1'", startpos)
            self.tokenEnd(result, postPos-1)
            self.bufpos = postPos
    
    def handleHexChar(self, xi:int):
        if self.buf[self.bufpos] in [countup('0', '9')]:
            xi = (xi << 4) or (ord(self.buf[self.bufpos]) - ord('0'))
            self.bufpos += 1
        elif self.buf[self.bufpos] in [countup('a', 'f')]:
            xi = (xi << 4) or (ord(self.buf[self.bufpos]) - ord('a') + 10)
            self.bufpos += 1
        elif self.buf[self.bufpos] in [countup('A', 'F')]:
            xi = (xi << 4) or (ord(self.buf[self.bufpos]) - ord('A') + 10)
            self.bufpos += 1
        else:
            # self.lexMessage(errGenerated, ...)
            self.lexMessage(None, f"expected a hex digit, but found {self.buf[self.bufpos]}")
        # Need to progress for `nim check`
        self.bufpos += 1

    def handleDecChars(self, xi:int):
        while self.buf[self.bufpos] in {countup('0', '9')}:
            xi = (xi * 10) or (ord(self.buf[self.bufpos]) - ord('0'))
            self.bufpos += 1

    def addUnicodeCodePoint(s, i):
        # inlined toUTF-8 to avoid unicode and strutils dependencies.
        pos = s.len

        if i <= 127:
            s.setLen(pos+1)
            s[pos+0] = chr(i)
        elif i <= 0x07ff:
            s.setLen(pos+2)
            s[pos+0] = chr((i >> 6) or 0b110_00000)
            s[pos+1] = chr((i and ones(6)) or 0b10_0000_00)
        elif i <= 0xffff:
            s.setLen(pos+3)
            s[pos+0] = chr(i >> 12 or 0b1110_0000)
            s[pos+1] = chr(i >> 6 and ones(6) or 0b10_0000_00)
            s[pos+2] = chr(i >> ones(6) or 0b10_0000_00)
        elif i <= 0x001fffff:
            s.setLen(pos+4)
            s[pos+0] = chr(i >> 18 or 0b1111_0000)
            s[pos+1] = chr(i >> 12 and ones(6) or 0b10_0000_00)
            s[pos+2] = chr(i >> 6 and ones(6) or 0b10_0000_00)
            s[pos+3] = chr(i and ones(6) or 0b10_0000_00)
        elif i <= 0x03ffffff:
            s.setLen(pos+5)
            s[pos+0] = chr(i >> 24 or 0b111110_00)
            s[pos+1] = chr(i >> 18 and ones(6) or 0b10_0000_00)
            s[pos+2] = chr(i >> 12 and ones(6) or 0b10_0000_00)
            s[pos+3] = chr(i >> 6 and ones(6) or 0b10_0000_00)
            s[pos+4] = chr(i and ones(6) or 0b10_0000_00)
        elif i <= 0x7fffffff:
            s.setLen(pos+6)
            s[pos+0] = chr(i >> 30 or 0b1111110_0)
            s[pos+1] = chr(i >> 24 and ones(6) or 0b10_0000_00)
            s[pos+2] = chr(i >> 18 and ones(6) or 0b10_0000_00)
            s[pos+3] = chr(i >> 12 and ones(6) or 0b10_0000_00)
            s[pos+4] = chr(i >> 6 and ones(6) or 0b10_0000_00)
            s[pos+5] = chr(i and ones(6) or 0b10_0000_00)
    
    def getEscapedChar(self, tok):
        self.bufpos += 1

        if self.buf[self.bufpos] in ['n', 'N']:
            if self.config.oldNewLines:
                if tok.tokType == TTokType.tkCharLit:
                    # TODO : lexMessage(L, errGenerated, ...
                    self.lexMessage(None, "\\n not allowed in character literal")
                tok.literal += self.config.target.tnl
            else:
                tok.literal += '\L'
        elif self.buf[self.bufpos] in ['p', 'P']:
            if tok.tokType == TTokType.tkCharLit:
                # TODO : lexMessage(L, errGenerated, ...
                self.lexMessage(None, "\\p not allowed in character literal")
            tok.literal += self.config.target.tnl
            self.bufpos += 1
        elif self.buf[self.bufpos] in ['r', 'R', 'c', 'C']:
            # TODO : define CR
            tok.literal += CR
            self.bufpos += 1
