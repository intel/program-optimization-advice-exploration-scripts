local opts = lprof:get_default_post_process_options()
opts.experiment_path = arg[2]

-- initialize cluster
local cluster = lprof_cluster.new (opts.experiment_path, opts, "Cluster")

-- iterate nodes to work on them one by one
local walltime = nil
for _, node in pairs (cluster:get_nodes()) do
   node:build_results()

   local node_results = node:get_results()
   local node_walltime = node_results:get_walltime_timer()
   if walltime == nil or walltime < node_walltime then
      walltime = node_walltime
   end

   node:unload_results()
end -- nodes

cluster:free()

print (walltime)

return 0
