import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: '/app/' — Python HTTP サーバからの配信パスに合わせる
// outDir: '../src/personal_mcp/web/app' — Python package 内 handoff path (#444)
export default defineConfig({
  plugins: [react()],
  base: "/app/",
  build: {
    outDir: "../src/personal_mcp/web/app",
    emptyOutDir: false, // true にすると web/app/ ごと削除されるため禁止
  },
});
