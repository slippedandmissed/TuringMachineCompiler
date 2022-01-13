#pragma once
#include <string>
#include <vector>
#include <istream>

#define FOR_ALL_TOKEN_TYPES \
    X(tok_eof)              \
    X(tok_space)            \
    X(tok_symbol)           \
    X(tok_identifier)       \
    X(tok_pos_int)          \
    X(tok_neg_int)          \
    X(tok_pos_double)       \
    X(tok_neg_double)       \
    X(tok_comment)          \
    X(tok_function)         \
    X(tok_return)

struct PositionInFile
{
    // Zero-indexed
    int row;
    int col;
};

enum TokenType
{
#define X(t) t,
    FOR_ALL_TOKEN_TYPES
#undef X
};

class Token
{
public:
    static std::string typeToString(TokenType);

public:
    TokenType type;
    std::string stringValue;
    long long intValue;
    double doubleValue;

    // Inclusive
    int startIndex;
    PositionInFile startPos;

    // Non-inclusive
    int endIndex;
    PositionInFile endPos;

    std::string toString(void);
};

class Lexer
{
private:
    std::istream *stream;
    int index{0};
    PositionInFile prevPos;
    PositionInFile pos{0, 0};
    char lastChar;
    char nextChar(void);
    Token getNextToken(void);
    Lexer();

public:
    Lexer(std::istream *stream);
    std::vector<Token> getAllTokens(void);
};