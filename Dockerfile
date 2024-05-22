# Use an official Node.js runtime as a parent image
FROM python:bookworm

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in package.json
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PORT_LABEL=7210
ENV PRINTER_URL=http://1.2.3.4:1700

# Run the API on container startup
CMD ["python", "./server.py"]
