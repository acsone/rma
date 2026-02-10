Managing return reasons at the batch level streamlines the RMA process, especially
when processing multiple items returned for the same reason.

This addon extends the RMA Batch functionality by introducing a reason field that
can be set at the batch level. When a reason is assigned to a batch:

- Any new RMAs created within that batch automatically inherit the batch's reason
- Existing RMAs without a reason can be updated to use the batch's reason through
  the batch form
- Individual RMAs can override the batch reason if needed

This simplifies the process of managing returns with consistent reasons and
reduces manual data entry for RMA processors.

