import java.util.ArrayList;
import java.util.Date;

public class BlockFunction {

    public String hash;
    public String previousHash;
    public String merkleRoot;
    public ArrayList<String> extendRoot;
    public ArrayList<String> extendNameList = new ArrayList<>();
    public ArrayList<ArrayList<Transaction>> transactionsTreeList = new ArrayList<>();
    public ArrayList<Transaction> transactions = new ArrayList<Transaction>(); //our data will be a simple message.
    public long timeStamp;
    public int nonce;

    //Block Constructor.
    public BlockFunction(String previousHash ) {
        this.previousHash = previousHash;
        this.timeStamp = new Date().getTime();
        this.hash = calculateHash(); //Making sure we do this after we set the other values.
    }

    //Calculate new hash based on blocks contents
    public String calculateHash() {
        String calculatedhash = StringUtil.applySha256(
                previousHash +
                        Long.toString(timeStamp) +
                        Integer.toString(nonce) +
                        merkleRoot
        );
        return calculatedhash;
    }

    //Increases nonce value until hash target is reached.
    public void mineBlock(int difficulty) {
        extendRoot.clear();
        merkleRoot = StringUtil.getMerkleRoot(transactions);
        for (int i = 0; i < extendNameList.size(); i++){
            extendRoot.add(StringUtil.getMerkleRoot(transactionsTreeList.get(i)));
        }
        for (int i = 0; i < extendRoot.size(); i++){
            merkleRoot += extendRoot.get(0);
        }
        String target = StringUtil.getDificultyString(difficulty); //Create a string with difficulty * "0"
        while(!hash.substring( 0, difficulty).equals(target)) {
            nonce ++;
            hash = calculateHash();
        }
        System.out.println("Block Mined!!! : " + hash);
    }

    //Add transactions to this block
    public boolean addTransaction(Transaction transaction) {
        if(transaction == null) return false;
        //process transaction and check if valid, unless block is genesis block then ignore.
        try {
            if (!transaction.type.equals("token")){
                if (extendNameList.contains(transaction.type)){
                    String result = callOracle(transaction.type);
                    int index = extendNameList.indexOf("transaction.type");
                    ArrayList<Transaction> extendTran = transactionsTreeList.get(index);
                    extendTran.add(new Transaction(transaction.sender,transaction.reciepient,transaction.value,transaction.inputs,transaction.type,result));
                }
            }
        }catch (NullPointerException e){
        }

        if((previousHash != "0")) {
            if((transaction.processTransaction() != true)) {
                System.out.println("Transaction failed to process. Discarded.");
                return false;
            }
        }
        transactions.add(transaction);
        System.out.println("Transaction Successfully added to Block");
        return true;
    }

    public String callOracle(String extend){
        Client client = new Client(extend);
        String result = client.connectOracle();
        return result;
    }

    public void listenOracle(){
        Client client = new Client("updateList");
        new Thread(){
            @Override
            public void run() {
                while (true){
                    String result = client.connectOracle();
                    if (!result.equals("")){
                        extendNameList.add(result);
                        transactionsTreeList.add(new ArrayList<>());
                    }
                }
            }
        }.start();
    }
}