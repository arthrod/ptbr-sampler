import cepPromise from "./cep-promise-node/dist/cep-promise.min.js";

// Process command line arguments
const args = process.argv.slice(2);

// Function to handle multiple CEPs
async function processCeps(ceps) {
    try {
        const results = await Promise.all(
            ceps.map(async (cepValue) => {
                try {
                    return await cepPromise(cepValue);
                } catch (error) {
                    return { error: error.message, cep: cepValue };
                }
            })
        );
        console.log(JSON.stringify(results));
    } catch (err) {
        console.error(JSON.stringify({ error: `Unexpected error: ${err.message}` }));
        process.exit(1);
    }
}

// Execute for all arguments
processCeps(args);