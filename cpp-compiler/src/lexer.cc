#include <iostream>
#include <cassert>
#include "lexer.h"

Lexer::Lexer(std::istream *stream) : stream(stream)
{
    lastChar = nextChar();
}

char Lexer::nextChar(void)
{
    char c;
    stream->get(c);
    if (!stream->good())
    {
        c = EOF;
    }
    index++;
    prevPos = pos;
    if (c == '\n')
    {
        pos.col = 0;
        pos.row++;
    }
    else
    {
        pos.col++;
    }
    return c;
}

Token Lexer::getNextToken(void)
{
    Token token;

    if (isspace(lastChar))
    {
        while (isspace(lastChar))
        {
            lastChar = nextChar();
        }
        token.type = tok_space;
        return token;
    }
    if (isalpha(lastChar))
    {
        std::string identifierStr(1, lastChar);
        while (isalnum((lastChar = nextChar())))
        {
            identifierStr += lastChar;
        }

        if (identifierStr == "function")
        {
            token.type = tok_function;
            return token;
        }
        if (identifierStr == "return")
        {
            token.type = tok_return;
            return token;
        }
        token.type = tok_identifier;
        token.stringValue = identifierStr;
        return token;
    }

    if (isdigit(lastChar) || lastChar == '.' || lastChar == '-')
    {
        bool isDouble = false;
        bool isNegative = lastChar == '-';
        std::string numStr;
        do
        {
            numStr += lastChar;
            if (lastChar == '.')
            {
                if (isDouble)
                {
                    break;
                }
                else
                {
                    isDouble = true;
                }
            }
            lastChar = nextChar();
        } while (isdigit(lastChar) || lastChar == '.');

        if (isDouble)
        {
            token.type = isNegative ? tok_neg_double : tok_pos_double;
            token.doubleValue = std::stod(numStr);
            return token;
        }

        token.type = isNegative ? tok_neg_int : tok_pos_int;
        token.intValue = std::stoll(numStr);
        return token;
    }

    if (lastChar == '#')
    {
        std::string commentStr;
        do
        {
            commentStr += lastChar;
            lastChar = nextChar();
        } while (lastChar != EOF && lastChar != '\n' && lastChar != '\r');
        token.type = tok_comment;
        token.stringValue = commentStr;
        return token;
    }

    if (lastChar == EOF)
    {
        token.type = tok_eof;
        return token;
    }

    token.type = tok_symbol;
    token.stringValue = lastChar;
    lastChar = nextChar();
    return token;
}

std::vector<Token> Lexer::getAllTokens(void)
{
    std::vector<Token> tokens;

    Token t;
    do
    {
        int startIndex = index - 1;
        PositionInFile startPos = prevPos;
        t = getNextToken();
        t.startIndex = startIndex;
        t.endIndex = index - 1;
        t.startPos = startPos;
        t.endPos = prevPos;
        tokens.push_back(t);
    } while (t.type != tok_eof);

    return tokens;
}

std::string Token::typeToString(TokenType t)
{
    switch (t)
    {
#define X(t) \
    case t:  \
        return #t;
        FOR_ALL_TOKEN_TYPES
#undef X
    }
    assert(false);
}

std::string Token::toString(void)
{
    std::string string = "Token<" + Token::typeToString(type) + "> ";
    string += "[" + std::to_string(startIndex) + "," + std::to_string(endIndex) + "] ";
    string += "[" + std::to_string(startPos.row) + ":" + std::to_string(startPos.col) + "," + std::to_string(endPos.row) + ":" + std::to_string(endPos.col) + "]";
    switch (type)
    {
    case tok_identifier:
    case tok_symbol:
    case tok_comment:
        string += " \"" + stringValue + "\""; // FIXME: Maybe try to escape this string
        break;
    case tok_pos_int:
    case tok_neg_int:
        string += " " + std::to_string(intValue);
        break;
    case tok_pos_double:
    case tok_neg_double:
        string += " " + std::to_string(doubleValue);
        break;
    default:
        break;
    }

    return string;
}