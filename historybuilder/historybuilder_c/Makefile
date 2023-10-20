.PHONY: all test clean

CC = gcc
CFLAGS=-Wall

all: historybuilder

historybuilder: main.o jenkins.o
	$(CC) $(CFLAGS) -o historybuilder main.o jenkins.o

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

jenkins.o: jenkins.c jenkins.h
	$(CC) $(CFLAGS) -c jenkins.c

test: test_main.c jenkins.o
	$(CC) $(CFLAGS) -o test_main test_main.c jenkins.o
	./test_main

clean:
	rm *.o historybuilder test_main
