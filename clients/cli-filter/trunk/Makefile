
EXE = dmail-cli-filter

SRC = src

# get all the .cpp files in this directory
SRCS = $(shell ls $(SRC)/*.cpp)
# assume we must create a .o for each of them
OBJS = $(SRCS:.cpp=.o)

CFLAGS = -Wall `gpgme-config --cflags`
LFLAGS = `gpgme-config --libs`


all: $(EXE)

$(EXE): $(OBJS)
	g++ -o $(EXE) $(OBJS) $(LFLAGS)

%.o: %.cpp
	g++ -o $@ -c $(CFLAGS) $^

clean:
	rm -f $(EXE) $(OBJS) *.*~ *~ *.bak core