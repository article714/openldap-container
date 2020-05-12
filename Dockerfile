FROM debian:buster-slim
LABEL maintainer="Apside"



# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Container tooling

COPY container /container

# container building

RUN /container/build.sh

# Expose ldap and ldaps ports
EXPOSE 389 636 5000

# LDAP data & conf in external volume
VOLUME /var/lib/ldap
# LOGS  in external volume
VOLUME /var/log
# Configuration  in external volume
VOLUME /container/config

# entrypoint  & default command
ENTRYPOINT [ "/container/entrypoint.sh" ]
CMD ["start"]

# healthcheck
HEALTHCHECK --interval=120s --timeout=2s --retries=5 CMD /container/check_running