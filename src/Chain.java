import java.security.Security;
import java.util.ArrayList;
import java.util.HashMap;

public class Chain {

    public static ArrayList<BlockFunction> blockchain = new ArrayList<BlockFunction>();
    public static HashMap<String,TransactionOutput> rcMap = new HashMap<String,TransactionOutput>();

    public static int difficulty = 3;
    public static float minimumTransaction = 0.1f;
    public static User userA;
    public static User userB;
    public static Transaction genesisTransaction;

    public static void main(String[] args) {
        Security.addProvider(new org.bouncycastle.jce.provider.BouncyCastleProvider()); //Setup Bouncey castle as a Security Provider
        
        userA = new User();
        userB = new User();
        User coinbase = new User();
        
        genesisTransaction = new Transaction(coinbase.publicKey, userA.publicKey, 100f, null,"token","");
        genesisTransaction.generateSignature(coinbase.privateKey);
        genesisTransaction.transactionId = "0";
        genesisTransaction.outputs.add(new TransactionOutput(genesisTransaction.reciepient, genesisTransaction.value, genesisTransaction.transactionId)); 
        rcMap.put(genesisTransaction.outputs.get(0).id, genesisTransaction.outputs.get(0)); 

        BlockFunction genesis = new BlockFunction("0");
        genesis.addTransaction(genesisTransaction);
        addBlock(genesis);

        //testing
        BlockFunction block1 = new BlockFunction(genesis.hash);
        block1.addTransaction(userA.processTX(userB.publicKey, 40f, "token",""));
        addBlock(block1);

        BlockFunction block2 = new BlockFunction(block1.hash);
        block2.addTransaction(userA.processTX(userB.publicKey, 0, "insurance",""));
        block2.addTransaction(userA.processTX(userB.publicKey, 0, "insurance",""));
        addBlock(block2);

        isChainValid();
    }

    public static Boolean isChainValid() {
        BlockFunction currentBlock;
        BlockFunction previousBlock;
        String hashTarget = new String(new char[difficulty]).replace('\0', '0');
        HashMap<String,TransactionOutput> temprcMap = new HashMap<String,TransactionOutput>();
        temprcMap.put(genesisTransaction.outputs.get(0).id, genesisTransaction.outputs.get(0));

        //loop through blockchain to check hashes:
        for(int i=1; i < blockchain.size(); i++) {

            currentBlock = blockchain.get(i);
            previousBlock = blockchain.get(i-1);
            //compare registered hash and calculated hash:
            if(!currentBlock.hash.equals(currentBlock.calculateHash()) ){
                System.out.println("#Current Hashes not equal");
                return false;
            }
            //compare previous hash and registered previous hash
            if(!previousBlock.hash.equals(currentBlock.previousHash) ) {
                System.out.println("#Previous Hashes not equal");
                return false;
            }
            //check if hash is solved
            if(!currentBlock.hash.substring( 0, difficulty).equals(hashTarget)) {
                System.out.println("#This block hasn't been mined");
                return false;
            }

            //loop thru blockchains transactions:
            TransactionOutput tempOutput;
            for(int t=0; t <currentBlock.transactions.size(); t++) {
                Transaction currentTransaction = currentBlock.transactions.get(t);

                if(!currentTransaction.verifiySignature()) {
                    System.out.println("#Signature on Transaction(" + t + ") is Invalid");
                    return false;
                }
                if(currentTransaction.getInputsValue() != currentTransaction.getOutputsValue()) {
                    System.out.println("#Inputs are note equal to outputs on Transaction(" + t + ")");
                    return false;
                }

                for(TransactionInput input: currentTransaction.inputs) {
                    tempOutput = temprcMap.get(input.transactionOutputId);

                    if(tempOutput == null) {
                        System.out.println("#Referenced input on Transaction(" + t + ") is Missing");
                        return false;
                    }

                    if(input.rc.value != tempOutput.value) {
                        System.out.println("#Referenced input Transaction(" + t + ") value is Invalid");
                        return false;
                    }

                    temprcMap.remove(input.transactionOutputId);
                }

                for(TransactionOutput output: currentTransaction.outputs) {
                    temprcMap.put(output.id, output);
                }

                if( currentTransaction.outputs.get(0).reciepient != currentTransaction.reciepient) {
                    System.out.println("#Transaction(" + t + ") output reciepient is not who it should be");
                    return false;
                }
                if( currentTransaction.outputs.get(1).reciepient != currentTransaction.sender) {
                    System.out.println("#Transaction(" + t + ") output 'change' is not sender.");
                    return false;
                }

            }

        }
        System.out.println("Blockchain is valid");
        return true;
    }

    public static void addBlock(BlockFunction newBlock) {
        newBlock.mineBlock(difficulty);
        blockchain.add(newBlock);
    }
}