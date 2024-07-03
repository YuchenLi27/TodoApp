FROM python:3.10

COPY ./ /app
WORKDIR /app
# eqaul to cd
RUN pip install -r requirements.txt
# the order of run and expose not matter, but copy and worked, and CMD's order are matter
EXPOSE 80
CMD [  "python3", "app.py" ]
