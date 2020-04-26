import java.security.*;
import java.security.spec.ECGenParameterSpec;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class User {

    public PrivateKey privateKey;
    public PublicKey publicKey;

    public HashMap<String,TransactionOutput> rcs = new HashMap<String,TransactionOutput>();

    public User(){
        generateKeyPair();
    }

    public void generateKeyPair() {
        try {
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("ECDSA","BC");
            SecureRandom random = SecureRandom.getInstance("SHA1PRNG");
            ECGenParameterSpec ecSpec = new ECGenParameterSpec("prime192v1");
            // Initialize the key generator and generate a KeyPair
            keyGen.initialize(ecSpec, random); 
            KeyPair keyPair = keyGen.generateKeyPair();
            privateKey = keyPair.getPrivate();
            publicKey = keyPair.getPublic();
        }catch(Exception e) {
            throw new RuntimeException(e);
        }
    }

    public float getBalance() {
        float total = 0;
        for (Map.Entry<String, TransactionOutput> item: Chain.rcMap.entrySet()){
            TransactionOutput rc = item.getValue();
            if(rc.isMine(publicKey)) { 
                rcs.put(rc.id,rc); //add it to our list of unspent transactions.
                total += rc.value ;
            }
        }
        return total;
    }

    public Transaction processTX(PublicKey _recipient,float value,String type,String extendScript) {
        if(getBalance() < value) {
            System.out.println("#Not Enough funds to send transaction. Transaction Discarded.");
            return null;
        }
        //create array list of inputs
        ArrayList<TransactionInput> inputs = new ArrayList<TransactionInput>();

        float total = 0;
        for (Map.Entry<String, TransactionOutput> item: rcs.entrySet()){
            TransactionOutput rc = item.getValue();
            total += rc.value;
            inputs.add(new TransactionInput(rc.id));
            if(total > value) break;
        }

        Transaction newTransaction = new Transaction(publicKey, _recipient , value, inputs, type, extendScript);
        newTransaction.generateSignature(privateKey);

        for(TransactionInput input: inputs){
            rcs.remove(input.transactionOutputId);
        }
        return newTransaction;
    }
}