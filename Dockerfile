FROM python

RUN mkdir -p /usr/src/site
WORKDIR /usr/src/site
COPY . .

RUN pip install -r requirements.txt
CMD [ "python", "Eriauth.py" ]
