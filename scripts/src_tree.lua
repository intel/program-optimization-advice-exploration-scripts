local asmf_name = arg[2]
local target_loop_id = tonumber (arg[3])

local proj = project.new ("loop_src")
local asmf = proj:load (asmf_name)

local function _rec_print_loop (loop)
    -- Stop recursivity
    if loop == nil then return end

    local parent = loop:get_parent()
    if parent ~= nil then
       _rec_print_loop (parent)
    end

    io.write (" <- ")

    local backedge_insn = loop:get_first_backedge_insn (loop)
    if backedge_insn ~= nil and
       backedge_insn:get_src_file_path() ~= nil then
       io.write (backedge_insn:get_src_file_path()..":")
       io.write (backedge_insn:get_src_line())
    elseif loop:get_src_file_path() ~= nil then
       io.write (loop:get_src_file_path()..":")
       local min, max = loop:get_src_lines()
       io.write (min.."-"..max)
    else
       io.write (string.format ("(no source info for loop %d)",
loop:get_id()))
    end
end

if asmf_name == nil or target_loop_id == nil then
    print (string.format ("Usage: %s /path/to/binary/file <loop ID>",
arg[1]))
    return 1
end

for fct in asmf:functions() do
    for loop in fct:loops() do
       if loop:get_id() == target_loop_id then
          io.write (loop:get_function():get_name())
          _rec_print_loop (loop)
          io.write ("\n")

          return 0
       end
    end
end
