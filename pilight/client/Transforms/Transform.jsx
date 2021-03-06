import PropTypes from 'prop-types';
import React from 'react';
import {
    Button,
    ButtonGroup,
    Checkbox,
    OverlayTrigger,
    Table,
    Tooltip,
} from 'react-bootstrap';

import * as types from '../types';

import Param from '../Params';
import {Variable} from '../Params/Variable';

import css from './Transform.scss';


export class Transform extends React.Component {
    static propTypes = {
        transform: types.ActiveTransform.isRequired,
        paramsDef: PropTypes.objectOf(types.ParamDef).isRequired,
        variablesByType: PropTypes.objectOf(
            PropTypes.arrayOf(
                PropTypes.shape({
                    id: PropTypes.number.isRequired,
                    name: PropTypes.string.isRequired,
                }),
            ),
        ).isRequired,
        description: PropTypes.string,
        moveDown: PropTypes.func.isRequired,
        moveUp: PropTypes.func.isRequired,
        onSave: PropTypes.func.isRequired,
        onDelete: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);
        // Do a JSON.stringify/parse to force a deep clone
        this.state = {
            params: JSON.parse(JSON.stringify(this.props.transform.params)),
            variableParams: JSON.parse(JSON.stringify(this.props.transform.variableParams)),
            modified: false,
        };
    }

    componentWillReceiveProps(nextProps) {
        if (JSON.stringify(nextProps.transform.params) !== JSON.stringify(this.props.transform.params) ||
            JSON.stringify(nextProps.transform.variableParams) !== JSON.stringify(this.props.transform.variableParams)) {
            // Reset the current value
            this.setState({
                params: JSON.parse(JSON.stringify(nextProps.transform.params)),
                variableParams: JSON.parse(JSON.stringify(nextProps.transform.variableParams)),
                modified: false,
            });
        }
    }

    onValueChange = (name) => (value) => {
        const newParams = Object.assign({}, this.state.params);
        newParams[name] = value;
        this.setState({
            params: newParams,
            modified: true,
        });
    };

    onVariableChange = (name) => (variable) => {
        const newVariableParams = Object.assign({}, this.state.variableParams);
        newVariableParams[name] = variable;
        this.setState({
            variableParams: newVariableParams,
            modified: true,
        });
    };

    onSave = () => {
        this.props.onSave(this.state.params, this.state.variableParams);
    };

    toggleVariable = (name) => (event) => {
        const newVariableParams = Object.assign({}, this.state.variableParams);
        if (event.target.checked) {
            newVariableParams[name] = {
                variable: '',
                multiply: 1.0,
                add: 0,
            };
        } else {
            delete newVariableParams[name];
        }
        this.setState({
            variableParams: newVariableParams,
            modified: true,
        });
    };

    render() {
        const paramRows = [];
        const params = this.props.transform.params;
        for (let name in params) {
            if (params.hasOwnProperty(name)) {
                let paramDef = null;
                if (this.props.paramsDef.hasOwnProperty(name)) {
                    paramDef = this.props.paramsDef[name];
                } else {
                    // Unknown param?
                    continue;
                }

                let variables = null;
                if (this.props.variablesByType.hasOwnProperty(paramDef.type)) {
                    variables = this.props.variablesByType[paramDef.type];
                }

                const value = this.state.params[name];
                const origValue = params[name];

                let isVariable = false;
                let variable = null;
                if (this.state.variableParams.hasOwnProperty(name)) {
                    isVariable = true;
                    variable = this.state.variableParams[name];
                }

                let paramControl = null;
                if (isVariable) {
                    paramControl = (
                        <Variable
                            onChange={this.onVariableChange(name)}
                            variable={variable}
                            variables={variables}
                        />
                    );
                } else {
                    paramControl = (
                        <Param
                            onChange={this.onValueChange(name)}
                            origValue={origValue}
                            paramDef={paramDef}
                            value={value}
                        />
                    );
                }

                const descriptionTooltip = (
                    <Tooltip id={paramDef.name}>{paramDef.description}</Tooltip>
                );

                paramRows.push(
                    <tr key={name}>
                        <td className={css.paramName}>
                            {paramDef.name}
                            {' '}
                            <OverlayTrigger placement="right" overlay={descriptionTooltip}>
                                <Button bsSize="xs" className="visible-xs-inline-block">?</Button>
                            </OverlayTrigger>
                        </td>
                        <td className={`hidden-xs ${css.paramDescription}`}>
                            <small>{paramDef.description}</small>
                        </td>
                        <td>
                            {!!variables ?
                                <Checkbox
                                    className={css.variableCheckbox}
                                    checked={isVariable}
                                    onChange={this.toggleVariable(name)}
                                /> : null
                            }
                        </td>
                        <td className={css.paramEditor}>
                            {paramControl}
                        </td>
                    </tr>
                );
            }
        }

        return (
            <Table bordered striped>
                <thead>
                <tr>
                    <th colSpan={4}>
                        {this.props.transform.name}
                        <div className={css.buttons}>
                            <Button
                                bsSize="xsmall"
                                bsStyle="danger"
                                onClick={this.props.onDelete}
                            >
                                Delete
                            </Button>
                            &nbsp;&nbsp;&nbsp;&nbsp;
                            <ButtonGroup>
                                <Button onClick={this.props.moveUp} bsSize="xsmall">Up</Button>
                                <Button onClick={this.props.moveDown} bsSize="xsmall">Down</Button>
                            </ButtonGroup>
                            {' '}
                            <Button
                                bsSize="xsmall"
                                bsStyle={this.state.modified ? "primary" : "default"}
                                onClick={this.onSave}
                            >
                                Save
                            </Button>
                        </div>
                    </th>
                </tr>
                </thead>
                <tbody>
                {paramRows}
                </tbody>
            </Table>
        )
    }
}
