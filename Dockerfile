FROM ubuntu:22.04

RUN apt-get update && apt-get -y upgrade

RUN apt-get install -y python3 python3-pip git

# SFML Build Dependencies
RUN apt-get install -y x11-xserver-utils g++ gcc cmake make libx11-dev libglu1-mesa-dev freeglut3-dev mesa-common-dev libogg-dev libopenal-dev libpthread-stubs0-dev libudev-dev libvorbis-dev libflac-dev libxrandr-dev libxcursor-dev libfreetype6-dev

RUN git clone -b 2.5.1 https://github.com/SFML/SFML.git

RUN cd SFML && mkdir build && cd build && cmake -G "Unix Makefiles" .. && make && make install

RUN apt-get install -y pybind11-dev

RUN git clone https://github.com/TravisAdsitt/SpellingMazeCPlusPlus.git

RUN cd SpellingMazeCPlusPlus && ls && mkdir build && cd build && cmake -G "Unix Makefiles" .. && make

RUN git clone https://github.com/TravisAdsitt/SpellingMaze.git

RUN cp -r /SpellingMazeCPlusPlus/res /
RUN cp -r /SpellingMazeCPlusPlus/build/*.so /SpellingMaze/

RUN cd SpellingMaze && git fetch && git checkout docker_testing && pip install -r requirements.txt && pip install flask natsort gunicorn

RUN apt-get install -y xvfb

ADD startup.sh /startup.sh
RUN chmod a+x /startup.sh

ENV DISPLAY=:99

WORKDIR /SpellingMaze
EXPOSE 8000:8000

CMD ["/startup.sh"]