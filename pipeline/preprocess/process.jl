using CSV
using ArgParse
using DataFrames
using JSON
using Dates
using Logging


function parse_commandline()
    s = ArgParseSettings()
    @add_arg_table! s begin
        "--datadir", "-d"
        help = "path to input files"
        default = "assets/raw/"
        "--processeddir", "-p"
        help = "files after processing"
        default = "assets/processed/"
        "--corpusfile", "-c"
        help = "corpus.txt file with text lines"
        default = "corpus.txt"
        "--testfile", "-t"
        help = "csv file with text lines"
        default = "test_set.csv"
    end
    return parse_args(s)
end

function corpus2mapping(datadir, processeddir, file)
    df = DataFrame(CSV.File(datadir * file; delim = "|"))

    @assert "acronym" in names(df) "The csv should contain an `acronym` columnname"
    @assert "expansion" in names(df) "The csv should contain an `expansion` columnname"
    mapping = unique(Pair.(df.expansion, df.acronym))

    @info "Found $(length(mapping)) mappings."
    timestamp = Dates.format(now(), "yyyy-mm-dd-HHMMSS_")
    path = processeddir * timestamp * "map.json"
    @info "Writing mappings to $path"
    open(path, "w") do f
        write(f, JSON.json(mapping))
    end
    return mapping
end


function create_trainset(corpuspath, mapping, processeddir)
    timestamp = Dates.format(now(), "yyyy-mm-dd-HHMMSS_")
    path = processeddir * timestamp * "train.csv"
    @info "Writing to $path"
    csvfile = open(path, "w")
    write(csvfile, "txt|label\n")
    open(corpuspath, "r") do f
        for line in eachline(f)
            for (expansion, abbr) in mapping
                if occursin(expansion, line)
                    line = replace(line, expansion => abbr)
                    write(csvfile, "$line|$expansion\n")
                end
            end
        end
    end
    close(csvfile)
end

function main()
    args = parse_commandline()
    datadir = args["datadir"]
    processeddir = args["processeddir"]
    testfile = args["testfile"]
    corpusfile = args["corpusfile"]
    @assert isfile(datadir * testfile) "The file $(datadir * testfile) does not exist"
    @assert isfile(datadir * corpusfile) "The file $(datadir * corpusfile) does not exist"
    io = open(processeddir * "processing.log", "a+")
    logger = SimpleLogger(io)

    with_logger(logger) do
        @info "Reading $testfile"
        mapping = corpus2mapping(datadir, processeddir, testfile)
        create_trainset(datadir * corpusfile, mapping, processeddir)
    end
    flush(io)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
