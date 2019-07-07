FROM alpine:3.7
RUN apk update && apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
   apk add --no-cache --update python3 && \
   pip3 install --upgrade pip setuptools
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 80 443 5000
ENTRYPOINT [ "/bin/sh","-c" ]
CMD ["flask run --host=0.0.0.0"]