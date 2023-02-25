FROM julia:1.8.5

RUN apt update
WORKDIR /app

COPY pipeline/preprocess/*.toml .
COPY assets /app/assets
COPY pipeline/preprocess/process.jl .
RUN julia -e 'using Pkg; Pkg.activate("."); Pkg.instantiate();'

ENTRYPOINT ["julia"]