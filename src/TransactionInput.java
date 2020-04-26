public class TransactionInput {
    public String transactionOutputId; //Reference to TransactionOutputs -> transactionId
    public TransactionOutput rc;

    public TransactionInput(String transactionOutputId) {
        this.transactionOutputId = transactionOutputId;
    }
}