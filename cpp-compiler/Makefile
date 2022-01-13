all:
	make debug

debug:
	make debug-lexer

test:
	make test-lexer

lexer:
	mkdir -p dist
	g++ -o dist/lexer.o -c src/lexer.cc

test-lexer:
	mkdir -p dist/test/lexer
	make debug-lexer
	g++ -g -o dist/test/test-lexer dist/lexer.o src/tests/lexer-test.cc

debug-lexer:
	mkdir -p dist
	g++ -g -o dist/lexer.o -c src/lexer.cc

clean:
	rm -rf dist
