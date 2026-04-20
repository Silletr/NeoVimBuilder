local repo = vim.env.COLORSCHEME_REPO or "EdenEast/nightfox.nvim"
local name = vim.env.COLORSCHEME_NAME or "duskfox"

return {
	repo,
	priority = 1000,
	lazy = false,
	config = function()
		-- Optional setup call (many plugins need this)
		local ok, plugin = pcall(require, repo:gsub(".nvim", "")):gsub("/", ".")
		if ok then
			plugin.setup({})
		end
		vim.cmd("colorscheme " .. name)
	end,
}
