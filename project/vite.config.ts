import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import nodePolyfills from 'rollup-plugin-polyfill-node';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      react(),
      nodePolyfills({
        include: ['node_modules/**/*.js'],
        polyfills: ['util', 'stream', 'path', 'process', 'events', 'buffer']
      }),
      nodeResolve({
        browser: true,
        preferBuiltins: false
      })
    ],
    optimizeDeps: {
      exclude: ['lucide-react'],
      include: ['mongodb'],
      esbuildOptions: {
        define: {
          global: 'globalThis'
        }
      }
    },
    define: {
      'global': 'globalThis',
      'process.env': process.env
    },
    resolve: {
      alias: {
        util: 'util',
        stream: 'stream-browserify',
        buffer: 'buffer',
        process: 'process/browser',
        events: 'events',
        path: 'path-browserify'
      }
    }
  };
});
