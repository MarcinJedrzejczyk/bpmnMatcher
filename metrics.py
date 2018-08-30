import bpmn_python.bpmn_diagram_metrics as metrics


def check_diagrams_metics(diag_a, diag_b, do_print=True):
    group = {}
    try:
        if do_print: print(
            "\n\tTNSE_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.TNSE_metric(diag_a), metrics.TNSE_metric(diag_b)))
        group["TNSE_metric"] = {"diag_a": metrics.TNSE_metric(diag_a), "diag_b": metrics.TNSE_metric(diag_b)}
    except:
        print("\nCan not calculate TNSE_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tTNIE_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.TNIE_metric(diag_a), metrics.TNIE_metric(diag_b)))
        group["TNIE_metric"] = {"diag_a": metrics.TNIE_metric(diag_a), "diag_b": metrics.TNIE_metric(diag_b)}
    except:
        print("\nCan not calculate TNIE_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tTNEE_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.TNEE_metric(diag_a), metrics.TNEE_metric(diag_b)))
        group["TNEE_metric"] = {"diag_a": metrics.TNEE_metric(diag_a), "diag_b": metrics.TNEE_metric(diag_b)}
    except:
        print("\nCan not calculate TNEE_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tTNE_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.TNE_metric(diag_a), metrics.TNE_metric(diag_b)))
        group["TNE_metric"] = {"diag_a": metrics.TNE_metric(diag_a), "diag_b": metrics.TNE_metric(diag_b)}
    except:
        print("\nCan not calculate TNE_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tNOA_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.NOA_metric(diag_a), metrics.NOA_metric(diag_b)))
        group["NOA_metric"] = {"diag_a": metrics.NOA_metric(diag_a), "diag_b": metrics.NOA_metric(diag_b)}
    except:
        print("\nCan not calculate NOA_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tNOAC_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.NOAC_metric(diag_a), metrics.NOAC_metric(diag_b)))
        group["NOAC_metric"] = {"diag_a": metrics.NOAC_metric(diag_a), "diag_b": metrics.NOAC_metric(diag_b)}
    except:
        print("\nCan not calculate NOAC_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tNOAJS_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.NOAJS_metric(diag_a), metrics.NOAJS_metric(diag_b)))
        group["NOAJS_metric"] = {"diag_a": metrics.NOAJS_metric(diag_a), "diag_b": metrics.NOAJS_metric(diag_b)}
    except:
        print("\nCan not calculate NOAJS_metric for one or both diagrams")

    try:
        if do_print:  print(
            "\n\tNumberOfNodes_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.NumberOfNodes_metric(diag_a),
                                                                       metrics.NumberOfNodes_metric(diag_b)))
        group["NumberOfNodes_metric"] = {"diag_a": metrics.NumberOfNodes_metric(diag_a),
                                         "diag_b": metrics.NumberOfNodes_metric(diag_b)}
    except:
        print("\nCan not calculate NumberOfNodes_metric for one or both diagrams")

    try:
        if do_print: print(
            "\n\tGatewayHeterogenity_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.GatewayHeterogenity_metric(diag_a),
                                                                             metrics.GatewayHeterogenity_metric(diag_b)))
        group["GatewayHeterogenity_metric"] = {"diag_a": metrics.GatewayHeterogenity_metric(diag_a),
                                               "diag_b": metrics.GatewayHeterogenity_metric(diag_b)}
    except:
        print("\nCan not calculate GatewayHeterogenity_metric for one or both diagrams")

    try:
        if do_print: print("\n\tCoefficientOfNetworkComplexity_metric: \ndiag_a:{}\ndiag_b:{}".format(
            metrics.CoefficientOfNetworkComplexity_metric(diag_a), metrics.CoefficientOfNetworkComplexity_metric(diag_b)))
        group["CoefficientOfNetworkComplexity_metric"] = {"diag_a": metrics.CoefficientOfNetworkComplexity_metric(diag_a),
                                                          "diag_b": metrics.CoefficientOfNetworkComplexity_metric(diag_b)}
    except:
        print("\nCan not calculate CoefficientOfNetworkComplexity_metric for one or both diagrams")

    try:
        if do_print:  print(
            "\n\tAverageGatewayDegree_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.AverageGatewayDegree_metric(diag_a),
                                                                              metrics.AverageGatewayDegree_metric(
                                                                                 diag_b)))
        group["AverageGatewayDegree_metric"] = {"diag_a": metrics.AverageGatewayDegree_metric(diag_a),
                                                "diag_b": metrics.AverageGatewayDegree_metric(diag_b)}
    except:
        print("\nCan not calculate AverageGatewayDegree_metric for one or both diagrams")

    try:
        if do_print: print("\n\tDurfeeSquare_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.DurfeeSquare_metric(diag_a),
                                                                                      metrics.DurfeeSquare_metric(diag_b)))
        group["DurfeeSquare_metric"] = {"diag_a": metrics.DurfeeSquare_metric(diag_a),
                                        "diag_b": metrics.DurfeeSquare_metric(diag_b)}
    except:
        print("\nCan not calculate DurfeeSquare_metric for one or both diagrams")
    try:
        if do_print: print("\n\tPerfectSquare_metric: \ndiag_a:{}\ndiag_b:{}".format(metrics.PerfectSquare_metric(diag_a),
                                                                                       metrics.PerfectSquare_metric(
                                                                                        diag_b)))
        group["PerfectSquare_metric"] = {"diag_a": metrics.PerfectSquare_metric(diag_a),
                                         "diag_b": metrics.PerfectSquare_metric(diag_b)}
    except:
        print("\nCan not calculate PerfectSquare_metric for one or both diagrams")

    return group
