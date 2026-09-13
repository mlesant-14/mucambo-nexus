/**
 * MUCAMBO Nexus - Node.js Launcher Wrapper
 * Enables 1-click launch via `npm start` or `npm run dev`
 */

const { spawn, execSync, exec } = require('child_process');
const os = require('os');

console.log('\x1b[36m%s\x1b[0m', '==============================================================================');
console.log('\x1b[32m%s\x1b[0m', '   MUCAMBO NEXUS - SISTEMA AUTONOMO DE ARBITRAGEM 24/7 (NPM RUNNER)');
console.log('\x1b[36m%s\x1b[0m', '==============================================================================');

// Determine Python executable (py launcher or python)
function getPythonCommand() {
    try {
        execSync('py --version', { stdio: 'ignore' });
        return 'py';
    } catch (e) {
        try {
            execSync('python --version', { stdio: 'ignore' });
            return 'python';
        } catch (err) {
            console.error('\x1b[31m%s\x1b[0m', '[ERRO] Python nao foi encontrado no sistema!');
            console.error('Por favor, certifique-se de que o Python esteja instalado.');
            process.exit(1);
        }
    }
}

const pyCmd = getPythonCommand();
console.log(`[*] Runtime detectado: ${pyCmd}`);

// Open browser automatically after a brief delay
setTimeout(() => {
    const url = 'http://localhost:8000';
    console.log('\x1b[33m%s\x1b[0m', `[*] Abrindo navegador em: ${url}`);
    
    const startCmd = process.platform === 'win32' ? `start ${url}` :
                     process.platform === 'darwin' ? `open ${url}` : `xdg-open ${url}`;
    exec(startCmd, () => {});
}, 1800);

// Launch main.py
const child = spawn(pyCmd, ['main.py'], {
    stdio: 'inherit',
    shell: false
});

child.on('close', (code) => {
    console.log(`[MUCAMBO] Processo encerrado com codigo ${code}`);
    process.exit(code);
});

// Clean shutdown handler
process.on('SIGINT', () => {
    console.log('\n[MUCAMBO] Encerrando sistema...');
    child.kill('SIGINT');
    process.exit(0);
});
