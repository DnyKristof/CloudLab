FROM python:lastest
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY src/facedetection.py facedetection.py
CMD python -u facedetection.py
