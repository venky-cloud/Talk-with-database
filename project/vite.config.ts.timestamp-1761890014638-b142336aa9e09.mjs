// vite.config.ts
import { defineConfig, loadEnv } from "file:///C:/Users/WELCOME/OneDrive/Documents/GitHub/Talk-with-database/project/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/WELCOME/OneDrive/Documents/GitHub/Talk-with-database/project/node_modules/@vitejs/plugin-react/dist/index.mjs";
import { nodeResolve } from "file:///C:/Users/WELCOME/OneDrive/Documents/GitHub/Talk-with-database/project/node_modules/@rollup/plugin-node-resolve/dist/es/index.js";
import nodePolyfills from "file:///C:/Users/WELCOME/OneDrive/Documents/GitHub/Talk-with-database/project/node_modules/rollup-plugin-polyfill-node/dist/index.js";
var vite_config_default = defineConfig(({ mode }) => {
  loadEnv(mode, process.cwd(), "");
  return {
    plugins: [
      react(),
      nodePolyfills({
        include: ["node_modules/**/*.js"],
        polyfills: ["util", "stream", "path", "process", "events", "buffer"]
      }),
      nodeResolve({
        browser: true,
        preferBuiltins: false
      })
    ],
    optimizeDeps: {
      exclude: ["lucide-react"],
      include: ["mongodb"],
      esbuildOptions: {
        define: {
          global: "globalThis"
        }
      }
    },
    define: {
      "global": "globalThis",
      "process.env": process.env
    },
    resolve: {
      alias: {
        util: "util",
        stream: "stream-browserify",
        buffer: "buffer",
        process: "process/browser",
        events: "events",
        path: "path-browserify"
      }
    }
  };
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxXRUxDT01FXFxcXE9uZURyaXZlXFxcXERvY3VtZW50c1xcXFxHaXRIdWJcXFxcVGFsay13aXRoLWRhdGFiYXNlXFxcXHByb2plY3RcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkM6XFxcXFVzZXJzXFxcXFdFTENPTUVcXFxcT25lRHJpdmVcXFxcRG9jdW1lbnRzXFxcXEdpdEh1YlxcXFxUYWxrLXdpdGgtZGF0YWJhc2VcXFxccHJvamVjdFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vQzovVXNlcnMvV0VMQ09NRS9PbmVEcml2ZS9Eb2N1bWVudHMvR2l0SHViL1RhbGstd2l0aC1kYXRhYmFzZS9wcm9qZWN0L3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnLCBsb2FkRW52IH0gZnJvbSAndml0ZSc7XHJcbmltcG9ydCByZWFjdCBmcm9tICdAdml0ZWpzL3BsdWdpbi1yZWFjdCc7XHJcbmltcG9ydCB7IG5vZGVSZXNvbHZlIH0gZnJvbSAnQHJvbGx1cC9wbHVnaW4tbm9kZS1yZXNvbHZlJztcclxuaW1wb3J0IG5vZGVQb2x5ZmlsbHMgZnJvbSAncm9sbHVwLXBsdWdpbi1wb2x5ZmlsbC1ub2RlJztcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZygoeyBtb2RlIH0pID0+IHtcclxuICAvLyBMb2FkIGVudiBmaWxlIGJhc2VkIG9uIGBtb2RlYCBpbiB0aGUgY3VycmVudCBkaXJlY3RvcnkuXHJcbiAgbG9hZEVudihtb2RlLCBwcm9jZXNzLmN3ZCgpLCAnJyk7XHJcbiAgXHJcbiAgcmV0dXJuIHtcclxuICAgIHBsdWdpbnM6IFtcclxuICAgICAgcmVhY3QoKSxcclxuICAgICAgbm9kZVBvbHlmaWxscyh7XHJcbiAgICAgICAgaW5jbHVkZTogWydub2RlX21vZHVsZXMvKiovKi5qcyddLFxyXG4gICAgICAgIHBvbHlmaWxsczogWyd1dGlsJywgJ3N0cmVhbScsICdwYXRoJywgJ3Byb2Nlc3MnLCAnZXZlbnRzJywgJ2J1ZmZlciddXHJcbiAgICAgIH0pLFxyXG4gICAgICBub2RlUmVzb2x2ZSh7XHJcbiAgICAgICAgYnJvd3NlcjogdHJ1ZSxcclxuICAgICAgICBwcmVmZXJCdWlsdGluczogZmFsc2VcclxuICAgICAgfSlcclxuICAgIF0sXHJcbiAgICBvcHRpbWl6ZURlcHM6IHtcclxuICAgICAgZXhjbHVkZTogWydsdWNpZGUtcmVhY3QnXSxcclxuICAgICAgaW5jbHVkZTogWydtb25nb2RiJ10sXHJcbiAgICAgIGVzYnVpbGRPcHRpb25zOiB7XHJcbiAgICAgICAgZGVmaW5lOiB7XHJcbiAgICAgICAgICBnbG9iYWw6ICdnbG9iYWxUaGlzJ1xyXG4gICAgICAgIH1cclxuICAgICAgfVxyXG4gICAgfSxcclxuICAgIGRlZmluZToge1xyXG4gICAgICAnZ2xvYmFsJzogJ2dsb2JhbFRoaXMnLFxyXG4gICAgICAncHJvY2Vzcy5lbnYnOiBwcm9jZXNzLmVudlxyXG4gICAgfSxcclxuICAgIHJlc29sdmU6IHtcclxuICAgICAgYWxpYXM6IHtcclxuICAgICAgICB1dGlsOiAndXRpbCcsXHJcbiAgICAgICAgc3RyZWFtOiAnc3RyZWFtLWJyb3dzZXJpZnknLFxyXG4gICAgICAgIGJ1ZmZlcjogJ2J1ZmZlcicsXHJcbiAgICAgICAgcHJvY2VzczogJ3Byb2Nlc3MvYnJvd3NlcicsXHJcbiAgICAgICAgZXZlbnRzOiAnZXZlbnRzJyxcclxuICAgICAgICBwYXRoOiAncGF0aC1icm93c2VyaWZ5J1xyXG4gICAgICB9XHJcbiAgICB9XHJcbiAgfTtcclxufSk7XHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBaVosU0FBUyxjQUFjLGVBQWU7QUFDdmIsT0FBTyxXQUFXO0FBQ2xCLFNBQVMsbUJBQW1CO0FBQzVCLE9BQU8sbUJBQW1CO0FBRTFCLElBQU8sc0JBQVEsYUFBYSxDQUFDLEVBQUUsS0FBSyxNQUFNO0FBRXhDLFVBQVEsTUFBTSxRQUFRLElBQUksR0FBRyxFQUFFO0FBRS9CLFNBQU87QUFBQSxJQUNMLFNBQVM7QUFBQSxNQUNQLE1BQU07QUFBQSxNQUNOLGNBQWM7QUFBQSxRQUNaLFNBQVMsQ0FBQyxzQkFBc0I7QUFBQSxRQUNoQyxXQUFXLENBQUMsUUFBUSxVQUFVLFFBQVEsV0FBVyxVQUFVLFFBQVE7QUFBQSxNQUNyRSxDQUFDO0FBQUEsTUFDRCxZQUFZO0FBQUEsUUFDVixTQUFTO0FBQUEsUUFDVCxnQkFBZ0I7QUFBQSxNQUNsQixDQUFDO0FBQUEsSUFDSDtBQUFBLElBQ0EsY0FBYztBQUFBLE1BQ1osU0FBUyxDQUFDLGNBQWM7QUFBQSxNQUN4QixTQUFTLENBQUMsU0FBUztBQUFBLE1BQ25CLGdCQUFnQjtBQUFBLFFBQ2QsUUFBUTtBQUFBLFVBQ04sUUFBUTtBQUFBLFFBQ1Y7QUFBQSxNQUNGO0FBQUEsSUFDRjtBQUFBLElBQ0EsUUFBUTtBQUFBLE1BQ04sVUFBVTtBQUFBLE1BQ1YsZUFBZSxRQUFRO0FBQUEsSUFDekI7QUFBQSxJQUNBLFNBQVM7QUFBQSxNQUNQLE9BQU87QUFBQSxRQUNMLE1BQU07QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLFFBQVE7QUFBQSxRQUNSLFNBQVM7QUFBQSxRQUNULFFBQVE7QUFBQSxRQUNSLE1BQU07QUFBQSxNQUNSO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
