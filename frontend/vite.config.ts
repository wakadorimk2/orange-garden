import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: '/app/' — Python HTTP サーバからの配信パスに合わせる
// outDir: 'dist' — #444 で最終配置先を確定し更新する
export default defineConfig({
  plugins: [react()],
  base: "/app/",
  build: {
    outDir: "dist",
  },
});
