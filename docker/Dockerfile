FROM eclipse-temurin:17.0.5_8-jdk
WORKDIR /app
RUN mkdir -p /app/tmp /app/logs && chown 1000:1000 /app/tmp /app/logs
RUN wget https://archive.apache.org/dist/activemq/5.17.3/apache-activemq-5.17.3-bin.tar.gz -O apache-activemq-5.17.3-bin.tar.gz \
    && tar --strip-components=1 -zxvf apache-activemq-5.17.3-bin.tar.gz \
    && chown -R 1000:1000 .
COPY --chown=1000:1000 conf/ ./conf
EXPOSE 8161
EXPOSE 61613
USER 1000
CMD ["/app/bin/activemq","console"]
