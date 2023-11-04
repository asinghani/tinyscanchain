module simple (
    input logic clk,
    input logic x,
    input logic [3:0] y,
    output logic [3:0] o
);

    logic [3:0] shreg;
    assign o = shreg ^ y;

    always_ff @(posedge clk) begin
        shreg <= {shreg[2:0], x};
    end

endmodule

