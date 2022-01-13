#include <sstream>
#include <cassert>
#include <iostream>
#include "../lexer.h"

void normalTest(void)
{
    std::istringstream testString = std::istringstream(
        "int add(int x, int y) {\n"
        "   return x + y;\n"
        "}");

    Lexer lexer(&testString);
    std::vector<Token> tokens = lexer.getAllTokens();

    for (Token token : tokens)
    {
        std::cout << token.toString() << std::endl;
    }
}

void numberTest(void)
{
    std::istringstream testString = std::istringstream(
        "123 -123 1.23 -1.23 1.2.3 -1.2.3 12-3");

    Lexer lexer(&testString);
    std::vector<Token> tokens = lexer.getAllTokens();

    for (Token token : tokens)
    {
        std::cout << token.toString() << std::endl;
    }
}


int main(int argc, char **argv)
{

    normalTest();

    return 0;
}