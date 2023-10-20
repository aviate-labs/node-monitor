.PHONY: all clean

CC = gcc
CFLAGS=-Wall

all: historybuilder

historybuilder: main.o
	$(CC) $(CFLAGS) -o historybuilder main.o

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

clean:
	rm *.o historybuilder
